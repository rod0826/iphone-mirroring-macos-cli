struct Failure: Error {
    let code: String
    let message: String
}

func fail(_ code: String, _ message: String) throws -> Never {
    throw Failure(code: code, message: message)
}

// Zero AX windows do not prove the phone is disconnected or a specific Space.
func requireObservableWindows<Window>(_ windows: [Window]) throws -> [Window] {
    guard !windows.isEmpty else {
        try fail("NO_ACCESSIBLE_WINDOWS", "The app is running but has no accessible windows. The window may be on another Space or hidden; move iPhone Mirroring to the current desktop and inspect again. Phone connection is unknown.")
    }
    return windows
}
