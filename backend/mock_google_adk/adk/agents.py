class Agent:
    def __init__(self, model, system_instruction, toolsets):
        self.model = model
        self.system_instruction = system_instruction
        self.toolsets = toolsets

class RunnerResponse:
    def __init__(self, text):
        self.text = text

class Runner:
    def __init__(self, agent, session_service, memory_service):
        self.agent = agent
        self.session_service = session_service
        self.memory_service = memory_service

    def run(self, session_id, message):
        # We need to call the mcp tools manually here to simulate the agent
        import mcp_server
        # We can simulate the process:
        username = message.split()[-1]
        data = mcp_server.scrape_github(username)
        analysis = mcp_server.analyze_profile(data)
        html = mcp_server.generate_card_html(username, data, analysis)
        url = mcp_server.save_card(username, html)
        return RunnerResponse(f"Card generated at {url}")
