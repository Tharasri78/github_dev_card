class McpToolset:
    def __init__(self, command, args, transport="stdio"):
        self.command = command
        self.args = args
        self.transport = transport
