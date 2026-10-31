// Apple exposes its toolbar lazily. Read first; reveal only when needed.
func resolveNavigationControl<Control>(read: () throws -> Control?, validate: () throws -> Void,
                                       reveal: () throws -> Void, wait: () -> Void) throws -> Control? {
    try validate()
    if let control = try read() { return control }
    try validate()
    try reveal()
    for _ in 0..<5 {
        wait()
        try validate()
        if let control = try read() { return control }
    }
    return nil
}

func performHomeSequence(presses: Int, press: () throws -> Void, wait: () -> Void) throws {
    for index in 0..<presses {
        if index > 0 { wait() }
        try press()
    }
}
