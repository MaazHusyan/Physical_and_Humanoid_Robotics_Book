import asyncio

from agents import Agent, Runner, RunContextWrapper

from gemini_model import geminiModel, config


agent = Agent(
    name="Master Agent",
    instructions="",
    model=geminiModel,
  )

async def main():
    
    while True:
        usrInp = input("Ask Something >>> ")
        
        if usrInp == "stop":
            break
        
        runResult =await Runner.run(
            agent,
            usrInp,
            run_config=config
        )
        print("LLM Output >>>",runResult.final_output)
    
if __name__ == "__main__":
    asyncio.run(main())
    
    
   
