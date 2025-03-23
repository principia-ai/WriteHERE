#!/usr/bin/env python3
from recursive.agent.prompts.base import PromptTemplate
from recursive.agent.prompts.base import prompt_register
from datetime import datetime

now = datetime.now()

@prompt_register.register_module()
class StoryWrtingNLReasonerEN(PromptTemplate):
    def __init__(self) -> None:
        system_message = ""

        content_template = """
The collaborative story-writing requirement to be completed: **{to_run_root_question}**

Your specific story design task to complete: **{to_run_task}**

---
The existing novel design conclusions are as follows:
```
{to_run_outer_graph_dependent}

{to_run_same_graph_dependent}
```

---
already-written novel:
```
{to_run_article}
```

---
You are an innovative professional writer collaborating with other professional writers to create a creative story that meets specified user requirements. Your task is to complete the story design tasks assigned to you, aiming to innovatively support the writing and design efforts of other writers, thereby contributing to the completion of the entire novel.

Attention!! Your design outcome should be logically consistent and coherent with the existing novel design conclusions.

# Design Hints
- **Structure**: The overall architecture of your narrative including plot development, pacing, and narrative arc (exposition, rising action, climax, falling action, resolution)
- **Character development**: How characters are introduced, built, and evolve throughout the story
- **Point of view**: The perspective from which the story is told (first person, third person limited, omniscient, etc.)
- **Setting**: The development of time and place, including worldbuilding element
- **Theme**: The underlying message or central idea being explored
- **Tone and mood**: The emotional atmosphere created and sustained throughout the work
- **Dialogue**: How characters speak and interact verbally
- **Writing style**: Your distinctive voice, including sentence structure, word choice, and figurative language
- **Narrative techniques**: Tools like foreshadowing, flashbacks, symbolism, and irony
- **Scene construction**: How individual scenes are built, including transitions between them

# Output Format
1. First, conduct thinking within `<think></think>`
2. Then, in `<result></result>`, write the design results in a structured and readable format, providing as much detail as possible.

Please complete the story design task **{to_run_task}** in a reasonable and innovative way, based on the requirements.
""".strip()
        super().__init__(system_message, content_template)

 
@prompt_register.register_module()
class StoryWritingReasonerFinalAggregate(PromptTemplate):
    def __init__(self) -> None:
        system_message = ""


# , **providing details which are useful for writing, do not provide too much un-useful details**.

        content_template = """
The collaborative story-writing requirement to be completed: **{to_run_root_question}**

Your specific story design task to complete: **{to_run_task}**

---
The existing novel design conclusions are as follows:
```
{to_run_outer_graph_dependent}

{to_run_same_graph_dependent}
```

---
already-written novel:
```
{to_run_article}
```

---
**The novel design conclusions you need to integrate and refine**, to give the final story design task: **{to_run_task}**:
```
{to_run_final_aggregate}
```

---
You are an innovative professional writer collaborating with other professional writers to create a creative story that meets specified user requirements. Your task is to **integrate and refine** the story design results provaiming to innovatively support the writing and design efforts of other writers, thereby contributing to the completion of the entire novel.ided by multiple novel designers, and complete the story design tasks assigned to you, ensuring that the final design is **innovative**, logically consistent, and coherent. You need resolving potential conflicts, enhancing connections between elements, and filling in gaps where necessary to produce a unified and compelling story, e.t.c. 

Attention!! Your design outcome should maintain **logical consistency** and **coherence** with the conclusions provided by the novel design, while elevating the quality of the overall novel design.  

# Integration and Refinement Requirements  
- **Integration**:  
  - Combine and synthesize input from multiple novel designer, ensuring all elements (e.g., plot, characters, themes) align into a unified and coherent whole.  
  - Identify and resolve logical inconsistencies or contradictions between Reasoners' results.  
  - Ensure that no critical design elements are omitted, and all aspects contribute to the story's progression and depth.  

- **Refinement**:  
  - Enhance the clarity, depth, and emotional resonance of the combined design.  
  - Fill in gaps or elaborate on areas that lack sufficient detail or development.  
  - Ensure the story’s tone, pacing, and style remain consistent throughout.  

- **Innovation and Impact**:  
  - Verify that the overall story design maintains originality and avoids clichés.  
  - Deepen universal or profound themes, ensuring they resonate with readers.  
  - Introduce subtle improvements or creative enhancements that elevate the story’s overall impact.  

  
# Design Hints
- **Structure**: The overall architecture of your narrative including plot development, pacing, and narrative arc (exposition, rising action, climax, falling action, resolution)
- **Character development**: How characters are introduced, built, and evolve throughout the story
- **Point of view**: The perspective from which the story is told (first person, third person limited, omniscient, etc.)
- **Setting**: The development of time and place, including worldbuilding element
- **Theme**: The underlying message or central idea being explored
- **Tone and mood**: The emotional atmosphere created and sustained throughout the work
- **Dialogue**: How characters speak and interact verbally
- **Writing style**: Your distinctive voice, including sentence structure, word choice, and figurative language
- **Narrative techniques**: Tools like foreshadowing, flashbacks, symbolism, and irony
- **Scene construction**: How individual scenes are built, including transitions between them


# Output Format  
1. First, conduct in-depth thinking within `<think></think>`, considering various possibilities during the thought process. Ensure to review and evaluate the input from all Reasoners, addressing inconsistencies and identifying areas for refinement or enhancement.  
2. Then, in `<result></result>`, write the **final** design results in a **structured and readable format**


Please complete the story design task **{to_run_task}** in a reasonable and innovative way, based on the requirements.
""".strip()
        super().__init__(system_message, content_template)