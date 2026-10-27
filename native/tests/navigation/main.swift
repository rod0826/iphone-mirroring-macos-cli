import Foundation

// The fake UI exposes the control only after pointer hover and an animation tick.
var hovered = false
var ticks = 0
let revealed: String? = try resolveNavigationControl(
    read: { hovered && ticks >= 2 ? "home-button" : nil }, validate: {},
    reveal: { hovered = true }, wait: { ticks += 1 })
precondition(revealed == "home-button", "Hidden toolbar must be revealed before lookup fails")

var moves = 0
let visible: String? = try resolveNavigationControl(read: { "visible-button" }, validate: {},
                                                   reveal: { moves += 1 }, wait: {})
precondition(visible == "visible-button" && moves == 0)

var attempts = 0
let absent: String? = try resolveNavigationControl(read: { attempts += 1; return nil }, validate: {},
                                                  reveal: {}, wait: {})
precondition(absent == nil && attempts == 6, "Initial read plus five bounded retries")

enum Changed: Error { case window }
var changed = false
var staleReads = 0
var stopped = false
do {
    let _: String? = try resolveNavigationControl(
        read: { staleReads += 1; return nil },
        validate: { if changed { throw Changed.window } },
        reveal: {}, wait: { changed = true })
} catch Changed.window { stopped = true }
precondition(stopped && staleReads == 1, "Never read/press after window or focus changes")

var forbiddenHover = false
var blocked = false
do {
    let _: String? = try resolveNavigationControl(read: { nil }, validate: { throw Changed.window },
                                                  reveal: { forbiddenHover = true }, wait: {})
} catch Changed.window { blocked = true }
precondition(blocked && !forbiddenHover)
print("5 navigation reveal regression cases passed")
