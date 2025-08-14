from dotenv import load_dotenv
from livekit import agents
from livekit.plugins.google.beta.realtime import RealtimeModel
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    noise_cancellation, 
    openai,
    google
)
from prompts import AGENT_INSTRUCTION

load_dotenv()

class Assistant(Agent):
    def __init__(self, proficiency_level: str = "intermediate", scenario: str = None) -> None:
        # Modify the agent instruction to include proficiency level
        modified_instruction = f"{AGENT_INSTRUCTION}\n\nThe learner's proficiency level is: {proficiency_level}. Adjust your language complexity accordingly."
        if scenario:
            modified_instruction += f"\n\nThe chosen scenario is: {scenario}. Start the role-play immediately after greeting."
        
        super().__init__(instructions=modified_instruction)

def get_user_preferences():
    """Get proficiency level and scenario from terminal input"""
    print("🎯 English Learning Session Setup")
    print("=" * 40)
    
    # Get proficiency level
    print("\nProficiency Levels:")
    print("1. Beginner")
    print("2. Intermediate") 
    print("3. Advanced")
    
    while True:
        try:
            level_choice = input("\nSelect your proficiency level (1-3): ").strip()
            if level_choice == "1":
                proficiency = "beginner"
                break
            elif level_choice == "2":
                proficiency = "intermediate"
                break
            elif level_choice == "3":
                proficiency = "advanced"
                break
            else:
                print("Please enter 1, 2, or 3")
        except KeyboardInterrupt:
            print("\nExiting...")
            exit()
    
    # Get scenario
    print(f"\nGreat! You selected: {proficiency.title()}")
    print("\nAvailable Scenarios:")
    scenarios = [
        "Job interview",
        "Ordering food at a restaurant",
        "Booking a hotel or flight", 
        "Making small talk with a new friend",
        "Business meeting",
        "Shopping at a store",
        "Asking for directions",
        "Doctor's appointment",
        "Phone conversation with customer service"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario}")
    print(f"{len(scenarios) + 1}. Custom scenario")
    
    while True:
        try:
            scenario_choice = input(f"\nSelect a scenario (1-{len(scenarios) + 1}): ").strip()
            
            if scenario_choice.isdigit():
                choice_num = int(scenario_choice)
                if 1 <= choice_num <= len(scenarios):
                    selected_scenario = scenarios[choice_num - 1]
                    break
                elif choice_num == len(scenarios) + 1:
                    selected_scenario = input("Enter your custom scenario: ").strip()
                    if selected_scenario:
                        break
                    else:
                        print("Please enter a scenario description")
                        continue
                else:
                    print(f"Please enter a number between 1 and {len(scenarios) + 1}")
            else:
                print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nExiting...")
            exit()
    
    print(f"\n✅ Setup Complete!")
    print(f"📚 Proficiency: {proficiency.title()}")
    print(f"🎭 Scenario: {selected_scenario}")
    print(f"🚀 Starting session...\n")
    
    return proficiency, selected_scenario

async def entrypoint(ctx: agents.JobContext):
    # Get user preferences from terminal
    proficiency_level, scenario = get_user_preferences()
    
    # Create customized session instruction
    customized_session_instruction = f"""
    Welcome to your English learning session!
    
    Your proficiency level: {proficiency_level.title()}
    Selected scenario: {scenario}
    
    Let's begin the role-play. I'll act as the other person in this scenario, and you can practice your English with me. 
    Don't worry about making mistakes - I'm here to help you improve!
    
    Ready? Let's start!
    """
    
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            voice="Puck",
            model="gemini-2.0-flash-exp",
            temperature=0.8
        )
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(proficiency_level=proficiency_level, scenario=scenario),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(
        instructions=customized_session_instruction
    )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))