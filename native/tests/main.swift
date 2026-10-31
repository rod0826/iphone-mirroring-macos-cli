precondition(isSharingIndicator(title: "Window", childTitles: ["WindowSharingSessionButton"], width: 66, height: 20))
precondition(!isSharingIndicator(title: "Window", childTitles: [], width: 66, height: 20))
precondition(!isSharingIndicator(title: "Window", childTitles: ["WindowSharingSessionButton"], width: 316, height: 696))
precondition(!isSharingIndicator(title: "Settings", childTitles: ["WindowSharingSessionButton"], width: 66, height: 20))
precondition(!isSharingIndicator(title: "Window", childTitles: ["WindowSharingSessionButton", "Confirm"], width: 66, height: 20))
print("5 native sharing-indicator policy cases passed")

let observed = try requireObservableWindows(["main-window"])
precondition(observed == ["main-window"])
var rejectedEmptyWindows = false
do { let _: [String] = try requireObservableWindows([]) }
catch let error as Failure { rejectedEmptyWindows = error.code == "NO_ACCESSIBLE_WINDOWS" }
precondition(rejectedEmptyWindows)
print("2 observation-window regression cases passed")
