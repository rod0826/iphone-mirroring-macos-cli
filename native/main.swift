import AppKit
import ApplicationServices
import Foundation

// No private Apple frameworks, entitlement injection, or phone-side services.
let bundleID = "com.apple.ScreenContinuity"
let appPath = "/System/Applications/iPhone Mirroring.app"
var ipcDirectory: URL?
var requestExpiry: Date?
let inputSource = CGEventSource(stateID: .hidSystemState)

struct Failure: Error {
    let code: String
    let message: String
}

func fail(_ code: String, _ message: String) throws -> Never {
    throw Failure(code: code, message: message)
}

func attribute(_ element: AXUIElement, _ name: String) -> CFTypeRef? {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, name as CFString, &value) == .success else { return nil }
    return value
}

func elements(_ element: AXUIElement, _ name: String) -> [AXUIElement] {
    attribute(element, name) as? [AXUIElement] ?? []
}

func text(_ element: AXUIElement, _ name: String) -> String {
    attribute(element, name) as? String ?? ""
}

func frame(_ element: AXUIElement) -> CGRect? {
    guard let origin = attribute(element, kAXPositionAttribute),
          let size = attribute(element, kAXSizeAttribute),
          CFGetTypeID(origin) == AXValueGetTypeID(),
          CFGetTypeID(size) == AXValueGetTypeID() else { return nil }
    var point = CGPoint.zero
    var dimensions = CGSize.zero
    guard AXValueGetValue(unsafeBitCast(origin, to: AXValue.self), .cgPoint, &point),
          AXValueGetValue(unsafeBitCast(size, to: AXValue.self), .cgSize, &dimensions)
    else { return nil }
    return CGRect(origin: point, size: dimensions)
}

func frameJSON(_ rectangle: CGRect) -> [String: Double] {
    ["x": rectangle.minX, "y": rectangle.minY,
     "width": rectangle.width, "height": rectangle.height]
}

func running() throws -> NSRunningApplication {
    let applications = NSRunningApplication.runningApplications(withBundleIdentifier: bundleID)
    guard applications.count == 1, let app = applications.first else {
        try fail("APP_NOT_RUNNING", "Launch iPhone Mirroring first; only one app instance is supported.")
    }
    return app
}

func requireAccessibility() throws {
    guard AXIsProcessTrusted() else {
        try fail("ACCESSIBILITY_REQUIRED",
                 "Grant Accessibility access to IPhoneMirroringCLI.app in System Settings > Privacy & Security > Accessibility, then rerun doctor. This tool never grants permissions.")
    }
}

func windows(_ app: NSRunningApplication) throws -> [AXUIElement] {
    try requireAccessibility()
    let root = AXUIElementCreateApplication(app.processIdentifier)
    AXUIElementSetMessagingTimeout(root, 1)
    var value: CFTypeRef?
    let error = AXUIElementCopyAttributeValue(root, kAXWindowsAttribute as CFString, &value)
    guard error == .success, let items = value as? [AXUIElement] else {
        try fail("AX_READ_FAILED", "Cannot read app windows (AX error \(error.rawValue)).")
    }
    return items
}

func windowJSON(_ window: AXUIElement) -> [String: Any] {
    var result: [String: Any] = [
        "title": text(window, kAXTitleAttribute),
        "identifier": text(window, kAXIdentifierAttribute),
        "minimized": attribute(window, kAXMinimizedAttribute) as? Bool ?? false
    ]
    if let bounds = frame(window) { result["frame"] = frameJSON(bounds) }
    return result
}

func inspect(_ window: AXUIElement) -> [String: Any] {
    var nodes = [[String: Any]]()
    var truncated = false
    let deadline = Date().addingTimeInterval(3)
    func walk(_ element: AXUIElement, _ depth: Int) {
        if nodes.count >= 300 || Date() >= deadline { truncated = true; return }
        var node: [String: Any] = ["depth": depth, "role": text(element, kAXRoleAttribute)]
        for (key, name) in [("title", kAXTitleAttribute), ("identifier", kAXIdentifierAttribute),
                            ("description", kAXDescriptionAttribute), ("value", kAXValueAttribute)] {
            let value = text(element, name)
            if !value.isEmpty { node[key] = String(value.prefix(2000)) }
        }
        if let bounds = frame(element) { node["frame"] = frameJSON(bounds) }
        nodes.append(node)
        let children = elements(element, kAXChildrenAttribute)
        if depth >= 8 { if !children.isEmpty { truncated = true }; return }
        for child in children { walk(child, depth + 1) }
    }
    walk(window, 0)
    return ["nodes": nodes, "truncated": truncated, "max_nodes": 300, "max_depth": 8]
}

func target(_ app: NSRunningApplication) throws -> (AXUIElement, CGRect) {
    let items = try windows(app).filter { window in
        guard let bounds = frame(window) else { return true }
        return !isSharingIndicator(title: text(window, kAXTitleAttribute),
            childTitles: elements(window, kAXChildrenAttribute).map { text($0, kAXTitleAttribute) },
            width: bounds.width, height: bounds.height)
    }
    guard items.count == 1, let window = items.first else {
        try fail("AMBIGUOUS_WINDOW", "Expected exactly one app window. Close settings/dialogs and inspect again.")
    }
    let identifier = text(window, kAXIdentifierAttribute).lowercased()
    let title = text(window, kAXTitleAttribute).lowercased()
    if identifier.contains("onboarding") || title.contains("시작하기") || title.contains("get started") {
        try fail("SETUP_REQUIRED", "Complete the Apple iPhone Mirroring setup manually before sending input.")
    }
    let hasSheet = elements(window, kAXChildrenAttribute).contains { text($0, kAXRoleAttribute) == kAXSheetRole }
    if title == "settings" || title == "설정" || hasSheet ||
        (attribute(window, kAXModalAttribute) as? Bool ?? false) {
        try fail("DIALOG_OPEN", "Dismiss app settings or authentication dialogs manually.")
    }
    guard identifier == "iphone-mirroring-main" else {
        try fail("UNKNOWN_WINDOW", "Expected the verified iphone-mirroring-main window; inspect before using input.")
    }
    guard !(attribute(window, kAXMinimizedAttribute) as? Bool ?? false),
          let bounds = frame(window), bounds.width > 100, bounds.height > 100 else {
        try fail("WINDOW_UNAVAILABLE", "Target window is minimized or has no usable frame.")
    }
    return (window, bounds)
}

func assertFocus(_ app: NSRunningApplication) throws {
    if let expiry = requestExpiry, Date() >= expiry {
        try fail("REQUEST_EXPIRED", "Request expired; no further input was posted. Inspect before retrying.")
    }
    guard NSWorkspace.shared.frontmostApplication?.processIdentifier == app.processIdentifier else {
        try fail("FOCUS_LOST", "iPhone Mirroring is not foreground; no further input was posted.")
    }
}

func post(_ event: CGEvent?, _ app: NSRunningApplication) throws {
    try assertFocus(app)
    guard let event else { try fail("EVENT_FAILED", "Could not create input event.") }
    event.post(tap: .cghidEventTap)
}

func key(_ code: CGKeyCode, _ flags: CGEventFlags, _ app: NSRunningApplication) throws {
    guard let down = CGEvent(keyboardEventSource: inputSource, virtualKey: code, keyDown: true),
          let up = CGEvent(keyboardEventSource: inputSource, virtualKey: code, keyDown: false) else {
        try fail("EVENT_FAILED", "Could not create keyboard event.")
    }
    down.flags = flags; up.flags = flags
    // Check once for the pair; always release the posted key.
    try assertFocus(app)
    down.post(tap: .cghidEventTap); up.post(tap: .cghidEventTap)
}

func typeText(_ value: String, _ app: NSRunningApplication) throws {
    // Per-character Unicode events avoid pasteboard modification and long-event truncation.
    for character in value {
        var units = Array(String(character).utf16)
        guard let down = CGEvent(keyboardEventSource: nil, virtualKey: 0, keyDown: true),
              let up = CGEvent(keyboardEventSource: nil, virtualKey: 0, keyDown: false) else {
            try fail("EVENT_FAILED", "Could not create text event.")
        }
        down.flags = []; up.flags = []
        units.withUnsafeMutableBufferPointer { buffer in
            down.keyboardSetUnicodeString(stringLength: buffer.count, unicodeString: buffer.baseAddress)
            up.keyboardSetUnicodeString(stringLength: buffer.count, unicodeString: buffer.baseAddress)
        }
        try assertFocus(app)
        // Preserve Unicode instead of re-translating through the Mac's input method.
        down.postToPid(app.processIdentifier); up.postToPid(app.processIdentifier)
        Thread.sleep(forTimeInterval: 0.005)
    }
}

func findElement(_ root: AXUIElement, matching: (AXUIElement) -> Bool) -> AXUIElement? {
    var remaining = 300
    func visit(_ element: AXUIElement, _ depth: Int) -> AXUIElement? {
        guard remaining > 0, depth <= 8 else { return nil }
        remaining -= 1
        if matching(element) { return element }
        for child in elements(element, kAXChildrenAttribute) {
            if let found = visit(child, depth + 1) { return found }
        }
        return nil
    }
    return visit(root, 0)
}

func press(_ element: AXUIElement) throws {
    let result = AXUIElementPerformAction(element, kAXPressAction as CFString)
    if result != .success { try fail("AX_ACTION_FAILED", "App rejected UI action (\(result.rawValue)).") }
}

func navigate(_ operation: String, _ window: AXUIElement, _ app: NSRunningApplication) throws {
    try assertFocus(app)
    if operation == "home" || operation == "app-switcher" {
        let identifier = operation == "home" ? "app.grid.3x3" : "iphone.app.switcher"
        guard let expectedBounds = frame(window) else {
            try fail("WINDOW_UNAVAILABLE", "Navigation window has no usable frame.")
        }
        func validateNavigationTarget() throws {
            try assertFocus(app)
            let (current, bounds) = try target(app)
            guard CFEqual(window, current), bounds == expectedBounds else {
                try fail("WINDOW_CHANGED", "Navigation window changed; inspect before retrying.")
            }
        }
        let button = try resolveNavigationControl(
            read: { findElement(window, matching: { text($0, kAXIdentifierAttribute) == identifier }) },
            validate: validateNavigationTarget,
            reveal: {
                guard ![CGMouseButton.left, .right, .center].contains(where: {
                    CGEventSource.buttonState(.combinedSessionState, button: $0)
                }) else { try fail("POINTER_BUSY", "Release mouse buttons before navigation.") }
                let location = CGPoint(x: expectedBounds.midX, y: expectedBounds.minY + 20)
                let event = CGEvent(mouseEventSource: inputSource, mouseType: .mouseMoved,
                                    mouseCursorPosition: location, mouseButton: .left)
                event?.flags = []
                try post(event, app) // Hover only: no click or keyboard fallback.
            },
            wait: { Thread.sleep(forTimeInterval: 0.15) })
        guard let button else {
            try fail("UI_CONTROL_MISSING", "Navigation button stayed unavailable after hover. Move the pointer over the iPhone Mirroring toolbar and inspect; check the phone connection.")
        }
        try validateNavigationTarget()
        try press(button)
        return
    }
    let root = AXUIElementCreateApplication(app.processIdentifier)
    guard let value = attribute(root, kAXMenuBarAttribute), CFGetTypeID(value) == AXUIElementGetTypeID() else {
        try fail("UI_CONTROL_MISSING", "App menu bar is unavailable.")
    }
    let menu = unsafeBitCast(value, to: AXUIElement.self)
    let spotlight: (AXUIElement) -> Bool = { text($0, kAXTitleAttribute) == "Spotlight" }
    // SwiftUI menu items can be readable while closed but not dispatch actions.
    // Open the actual menu before invoking Spotlight.
    guard let view = findElement(menu, matching: {
        ["View", "보기"].contains(text($0, kAXTitleAttribute)) && text($0, kAXRoleAttribute) == kAXMenuBarItemRole
    }) else { try fail("UI_CONTROL_MISSING", "View menu is unavailable (tested locales: Korean and English).") }
    try press(view)
    Thread.sleep(forTimeInterval: 0.1)
    guard let item = findElement(view, matching: spotlight) else {
        try fail("UI_CONTROL_MISSING", "Spotlight menu action is unavailable.")
    }
    try assertFocus(app)
    try press(item)
}

func handle(_ input: [String: Any]) throws -> [String: Any] {
    guard let operation = input["operation"] as? String else {
        try fail("INVALID_ARGUMENT", "Missing operation.")
    }
    let allowed = ["doctor", "status", "inspect", "launch", "home", "app-switcher", "search", "type", "key", "click", "scroll"]
    guard allowed.contains(operation) else { try fail("INVALID_ARGUMENT", "Unknown operation.") }
    let dryRun = input["dry_run"] as? Bool ?? false
    let installed = FileManager.default.fileExists(atPath: appPath)
    if operation == "doctor" {
        let bundle = Bundle(path: appPath)
        return ["ok": true, "installed": installed, "bundle_id": bundleID,
                "app_version": bundle?.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "unknown",
                "accessibility_trusted": AXIsProcessTrusted(), "helper": CommandLine.arguments[0],
                "helper_bundle": Bundle.main.bundleURL.path,
                "running": !NSRunningApplication.runningApplications(withBundleIdentifier: bundleID).isEmpty,
                "connection": "unknown", "permission_prompted": false]
    }
    guard installed else { try fail("APP_MISSING", "Apple iPhone Mirroring is not installed at the expected system path.") }
    if operation == "launch" {
        if dryRun { return ["ok": true, "dry_run": true, "operation": operation] }
        var finished = false
        var launchError: Error?
        let configuration = NSWorkspace.OpenConfiguration()
        configuration.activates = true
        NSWorkspace.shared.openApplication(at: URL(fileURLWithPath: appPath), configuration: configuration) { _, error in
            launchError = error; finished = true
        }
        let deadline = Date().addingTimeInterval(5)
        while !finished && Date() < deadline { RunLoop.current.run(until: Date().addingTimeInterval(0.05)) }
        guard finished, launchError == nil else {
            try fail("LAUNCH_FAILED", launchError?.localizedDescription ?? "Launch timed out after 5 seconds.")
        }
        return ["ok": true, "operation": operation, "running": true, "connection": "unknown"]
    }
    let app = try running()
    if operation == "status" || operation == "inspect" {
        let items = try windows(app)
        var result: [String: Any] = ["ok": true, "pid": app.processIdentifier,
            "running": true, "frontmost": NSWorkspace.shared.frontmostApplication?.processIdentifier == app.processIdentifier,
            "connection": "unknown", "windows": items.map(windowJSON)]
        if operation == "inspect" { result["accessibility"] = items.map(inspect) }
        return result
    }
    let (window, bounds) = try target(app)
    // Validate all request fields before any activation or event posting.
    let value = input["text"] as? String ?? ""
    if operation == "type" || operation == "search" {
        guard !value.isEmpty, value.unicodeScalars.count <= 1000, !value.contains("\0"),
              value.allSatisfy({ String($0).utf16.count <= 20 }) else {
            try fail("INVALID_ARGUMENT", "Text must contain 1–1000 Unicode scalars without NUL or oversized graphemes.")
        }
    }
    let keyCodes: [String: CGKeyCode] = ["return": 36, "escape": 53, "tab": 48,
        "backspace": 51, "up": 126, "down": 125, "left": 123, "right": 124]
    let keyName = input["name"] as? String ?? ""
    if operation == "key" && keyCodes[keyName] == nil { try fail("INVALID_ARGUMENT", "Unsupported key.") }
    let x = input["x"] as? Double ?? -1, y = input["y"] as? Double ?? -1
    if operation == "click" {
        guard x.isFinite, y.isFinite, x >= 0, x < bounds.width,
              y >= 40, y < bounds.height - 20 else {
            try fail("OUT_OF_BOUNDS", "Click must be inside window content: x in [0,width), y in [40,height-20).")
        }
    }
    let direction = input["direction"] as? String ?? ""
    let pixels = input["pixels"] as? Int ?? 0
    if operation == "scroll" && (!(1...10000).contains(pixels) || !["up", "down", "left", "right"].contains(direction)) {
        try fail("INVALID_ARGUMENT", "Invalid scroll direction or pixel count.")
    }
    if dryRun { return ["ok": true, "dry_run": true, "operation": operation, "window": windowJSON(window)] }
    app.activate(options: [])
    let deadline = Date().addingTimeInterval(1)
    while NSWorkspace.shared.frontmostApplication?.processIdentifier != app.processIdentifier && Date() < deadline {
        RunLoop.current.run(until: Date().addingTimeInterval(0.02))
    }
    try assertFocus(app)
    // Geometry/window identity may have changed during activation; reject stale targeting.
    let (current, currentBounds) = try target(app)
    guard CFEqual(window, current), bounds == currentBounds else {
        try fail("WINDOW_CHANGED", "Target window changed during activation; inspect and retry.")
    }
    switch operation {
    case "home", "app-switcher": try navigate(operation, current, app)
    case "key": try key(keyCodes[keyName]!, [], app)
    case "type": try typeText(value, app)
    case "search":
        // Spotlight is a toggle. Establish Home first and let the remote
        // transition finish before opening it, including on repeated searches.
        try navigate("home", current, app)
        Thread.sleep(forTimeInterval: 0.6)
        _ = try target(app)
        try navigate(operation, current, app)
        Thread.sleep(forTimeInterval: 0.6)
        _ = try target(app)
        try typeText(value, app)
    case "click":
        let location = CGPoint(x: bounds.minX + x, y: bounds.minY + y)
        guard let down = CGEvent(mouseEventSource: inputSource, mouseType: .leftMouseDown, mouseCursorPosition: location, mouseButton: .left),
              let up = CGEvent(mouseEventSource: inputSource, mouseType: .leftMouseUp, mouseCursorPosition: location, mouseButton: .left) else {
            try fail("EVENT_FAILED", "Could not create mouse event.")
        }
        down.flags = []; up.flags = []
        try assertFocus(app)
        down.post(tap: .cghidEventTap); up.post(tap: .cghidEventTap)
    case "scroll":
        let vertical = direction == "up" ? pixels : direction == "down" ? -pixels : 0
        let horizontal = direction == "left" ? pixels : direction == "right" ? -pixels : 0
        let event = CGEvent(scrollWheelEvent2Source: inputSource, units: .pixel, wheelCount: 2,
                            wheel1: Int32(vertical), wheel2: Int32(horizontal), wheel3: 0)
        event?.location = CGPoint(x: bounds.midX, y: bounds.midY)
        try post(event, app)
    default: try fail("INVALID_ARGUMENT", "Unsupported input operation.")
    }
    // Quartz delivery is asynchronous. Do not exit the short-lived app while
    // WindowServer is still consuming its events and sender audit identity.
    Thread.sleep(forTimeInterval: 0.2)
    return ["ok": true, "operation": operation,
            "delivery": ["home", "app-switcher", "search"].contains(operation) ? "requested" : "posted",
            "verified": false, "connection": "unknown",
            "note": "Mac UI action requested or events posted; verify the iPhone-side effect visually."]
}

func output(_ value: [String: Any], _ exitCode: Int32) -> Never {
    if let bytes = try? JSONSerialization.data(withJSONObject: value, options: [.sortedKeys]) {
        if let directory = ipcDirectory {
            try? bytes.write(to: directory.appendingPathComponent("response.json"), options: [.atomic])
        } else if let line = String(data: bytes, encoding: .utf8) { print(line) }
    }
    exit(exitCode)
}

do {
    let data: Data
    if CommandLine.arguments.count == 3 && CommandLine.arguments[1] == "--ipc" {
        let directory = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
        let attributes = try FileManager.default.attributesOfItem(atPath: directory.path)
        guard attributes[.type] as? FileAttributeType == .typeDirectory,
              (attributes[.ownerAccountID] as? NSNumber)?.uint32Value == getuid(),
              (attributes[.posixPermissions] as? NSNumber)?.intValue == 0o700 else {
            try fail("INVALID_IPC", "IPC directory must be a private directory owned by this user.")
        }
        ipcDirectory = directory
        data = try Data(contentsOf: directory.appendingPathComponent("request.json"))
    } else {
        data = FileHandle.standardInput.readDataToEndOfFile()
    }
    guard data.count <= 65536, let request = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
        try fail("INVALID_ARGUMENT", "Expected one JSON request object, at most 64 KiB.")
    }
    if ipcDirectory != nil {
        guard let expiry = request["expires_at"] as? Double,
              expiry > Date().timeIntervalSince1970,
              expiry <= Date().timeIntervalSince1970 + 15 else {
            try fail("REQUEST_EXPIRED", "IPC request is expired or has no valid deadline.")
        }
        requestExpiry = Date(timeIntervalSince1970: expiry)
    }
    output(try handle(request), 0)
} catch let error as Failure {
    output(["ok": false, "error": ["code": error.code, "message": error.message]], 1)
} catch {
    output(["ok": false, "error": ["code": "INVALID_REQUEST", "message": "Invalid JSON request."]], 1)
}
