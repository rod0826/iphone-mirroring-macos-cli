// macOS may expose a tiny sharing indicator as another AXWindow in this app.
// Ignore only the observed indicator shape, not arbitrary dialogs or windows.
func isSharingIndicator(title: String, childTitles: [String], width: Double, height: Double) -> Bool {
    title == "Window" && childTitles == ["WindowSharingSessionButton"] &&
        width > 0 && width <= 100 && height > 0 && height <= 40
}
