# Stream of Consciousness Notes
because I easily get distracted and often have an idea and just need a bucket (this file) to put it in case I need it later.
Also this is a sort of diary where I will formulate my prompts to claude as I try to figure out how I want to progress with this repo
since my infinite backlog continues to unfold and I find it challenging to go deep on one thread after I've exhausted myself with brainstorming and planning.
Also this is like therapy for me: trying to make sense of the ai landscape, figure out what I can generalize into similar conceptual buckets to preserve my sanity, ...

https://github.com/ZackHelms/learn-ai

## 8Aug2026
Experimenting with Claude Cowork (with "computer use" enabled so it can show me how to do things on my desktop computer if I ask)
    instead of Claude Code which is my typical interface I work with... I need to learn ins and outs of the other Claude interfaces.

Me: Typically I use claude code so it can access my git repository. I'd like to give claude cowork a try (I'm in that part of the windows 11 desktop app currently), for example the "computer use" feature (when it makes sense), and I have VSCode WSL2 Ubuntu 24.04 open on the right side of my screen in my local learn-ai git repository https://github.com/ZackHelms/learn-ai 
    Today I would like to finally get started with with doing and refining the first module of my learn-ai repo. Note that this learn-ai repo is one that I'm building out for my own personal learning, but in a way that others could use later (like my brother, my kids, my coworkers, etc). 
    For the first module I would like you to walk me through usage of the free versions of the top AI platforms: anthropic claude, openai chatgpt codex, google gemini, microsoft copilot. I'm primarily working in VSCode with wsl2/ubuntu so I want to walk through ways to access and use them there, but the module should also walk me through how to use the rich client versions for each and the web versions for each, with commentary on how each of those modes (web, app, vscode/ubuntu) differs when it comes to what can be done with the ai (for free), and how working with only one or perhaps 2 at the same time or all 3 can be useful (if true).
    Before we get started, ask me any clarifying questions to improve alignment between my intent and how you are hearing it (in case I have not communicated my intent as well as I should have).

CC: Q&A
1. Modules 00 and 01 are already written, and the repo's stated premise is local weak models + harness-agnostic. Where does this new commercial-platform module fit?
2. How should the finished module land in your repo? No local folder is connected to this session yet, and the repo is inside WSL2 (which the desktop bridge may not reach).
3. How hands-on should this be today? You said 'walk me through' - that could mean a doc I author, or a live session where I actually drive.
4. What does 'free' mean for this module, given you have paid Claude Code and a work Copilot license?

Me:
1. good catch, thanks! Lets re-think the repo wide premise; Not sure how to phrase it, but I'm thinking 
    "Track1" can contain the existing modules 00 & 01 and "Track1" premise can be "local weak models + harness-agnostic". I dont feel like working on that track right now though.
    "Track2" premise can be something like "what can I do in the free tier?" and the modules in this track can follow what I mentioned earlier (I'd like to work on this track right now).
    "Track3" premise can be something like "what can I do with Claude Pro $20/month?" and it can reinforce some of the concepts learned in modules in other tracks, or simply be where someone starts fresh if they like. This track would involve using the claude desktop app, mobile app, vscode, web app, claude design, and whatever else there is.
    Later, other tracks might get into the base paid tier for other providers (openai, gemini, github copilot), but they will have to wait until I either have a need to work on them (and will then shell out the $10-$20 for a month of experimenting with it, for example github copilot is what we have to use at work so that might be useful, and gemini might be useful to explore its audio video image (multimodal) ai tools to see if any of those might compliment my overall long term goals in a useful way)
2. can I create a project folder for this session in my windows filesystem and you use that locally here on my windows host (instead of spinning up a container or something remotely) and then just merge/push to main/remote and then in my wsl session I can git pull to get the updates (and vice versa I can push changes to remote main too .. so you might want to git pull in your local windows repo copy prior to any new updates you do.)
3. Live walkthrough now, doc written as we go
4. Strictly free tiers. I can keep you open in my desktop app here to the left for guidance if needed, and I could set up a free tier claude code account with a separate email address for working with & testing the parts that require free tier claude code; lets do the claude code free part last so we can work out any kinks in the module with the other providers first.

I watch Claude Cowork create folder `C:\Users\zmhel\gitrepos` where it presumably will clone the learn-ai repo.

Q&A:
    CC: How should my work reach your repo, given I can copy files to your Windows disk but can't run git there?
    Me: I dont understand. cant you run commands in power shell? what do you mean by 'restart this task on my computer instead'?
    CC: For the live walkthrough, how do you want me to see what's happening on your screen?
    Me: Computer use - I drive and observe your desktop

Me: lets restart this task on my computer, that sounds most efficient (right?). How do I do that without losing the session context thus far?
CC: start a new Cowork task, and before you type, use the "Run this task" picker at the top right and choose "On your computer". 
    (If you want that to be the default, Settings -> Cowork -> turn off "Run new tasks in the cloud".) If the picker doesn't appear, 
    the option isn't enabled on your account.
    Then copy/paste the handoff prompt `.claude/notes/202608081709-handoff-prompt-for-claude-cowork.md` contents into new cowork session.

I do that. I create `C:\Users\zmhel\claude-cowork-learn-ai` when it prompts me that cc would like to cowork in a folder and asks which one we should use.

Q&A:
    How do you want me to get read/write access to the learn-ai repo?
    why cant you do this in a powershell on my local windows pc? That should be a smoother option than trying to use windows filesystem via wsl2.
    Given I cannot run git, how should git operations be handled?
    Lets get the basics ironed out first. pause all other tasks and lets figure out why you are not working in a powershell for windows filesystem access.

Me:
    When I start the claude cowork session should I be specifying a project and/or folder to work in? would this still be you working in that folder via some linux container that is running on my windows pc via wsl2? I did: 
    Settings -> Cowork -> turn off "Run new tasks in the cloud" and selected default of 
    "Run this task" picker at the top right and choose "On your computer" so I dont understand why you are still running in a linux shell

Are we headed in the best direction?
Honest read, split by what you actually want to do:
- The track restructure is bulk git mv plus link rewrites. Cowork is a poor fit - I would be hand-editing files while you run every git command. Claude Code in your Ubuntu shell does this natively in a fraction of the time. You already identified this correctly.
- Track 2 Module 01 is the opposite. You are testing free-tier Gemini, Copilot, Codex, and Claude across VSCode, desktop apps, and web. That means browser automation, native desktop apps, and screenshots. Claude Code cannot do any of that. Cowork can. And you already planned to run the CLI commands yourself and paste output, so my lack of a WSL shell costs almost nothing there.
- inferred: the two halves of today's plan want different tools. Forcing both into one session is what has been generating friction for the last twenty minutes.

I restart claude desktop app (because it asked me to earlier and because the q&a went away).

Q&A:
    How do you want to split the work between Cowork and Claude Code?
    Split the work (Recommended)
    Do you want me to verify the WSL2 UNC path claim before we rely on it?
    yes

...

So the split you chose is now forced rather than optional:
|                                 | Tool               | Why                                                               |
| Track restructure               | Claude Code in WSL | native git, real repo access, brief already written               |
| Module 01 research and drafting | Cowork (here)      | browser, desktop apps, screenshots                                |
| Getting drafts into the repo    | you or Claude Code | I write to C:\Users\zmhel\claude-cowork-learn-ai, you copy across |
That staging step is mildly annoying but it decouples us from the restructure entirely - I can draft Module 01 now without touching files Claude Code is moving. Ordering no longer matters.
Let me start on Gemini...


### CLI
Meanwhile I /login to claude cli to run `.claude/notes/202608081741-handoff-prompt-1of2-for-claude-cli.md`

Lets go with the following layout (I'm assuming all the other dirs and files remain and this layout is just showing what changes.. i'm adding root README.md anyway to this list even though only its contents change a bit)
Since they are numbered directories they are easy for the reader to visually bucket which improves readability and does not add to the clutter/noise that otherwise might reduce readability.

README.md: gives overview of current state of the repo (ie tracks and modules within each that are available and those that are planned but not yet completed) with links so folks looking at it in a web browser can jump in to any $track/README.md or module to get an idea of what it is about.
track-01-local-models
    README.md: copy the premise from root readme into this readme. The root readme can still give a premise tagline but I want the root readme to be lean/concise/easy for the reader to get a quick overview idea of what each track gets into so reader can make a decision about which track best suits them.
    00-overview/
    01-local-model-lab/
track-02-free-tier
    README.md: I'm working on this repo's modules now (in a claude cowork session) and will start fleshing them out after this refactor is done.
track-03-claude-pro
    README.md: This tack's modules are a natural follow up to track02 that I'll probably want to work on next.

uncertainty6: The 'If you use a harness' text (in multiple files) should be moved into track01 as a note and selling point for the track. 
Track2 is aimed at someone who does not want to go as deep as track1 would take them, and it offers modules that someone with only an ipad or iphone could experiment with, so its a useful starting point for a certain segment of readers. My nephew Logan (middle school age) is one example of someone who fits this segment (he doesnt have a PC to do real dev work at and he has been experimenting on his own with free claude via web).
Track3 is aimed at someone who is paying $20/month for claude pro and wants to level up particular ai skills to see what is possible and highlights what is possible with claude paid tier vs free tier. My brother (44) is an example of someone who is a good candidate for this track; also, I am a good candidate for this track where I want to add some modules around creating sdk based agents that use Luna/Haiku tier models with intentionally chosen effort levels (escalation of effort level when applicable) with evals (ie unit tests or benchmarks for some basic task I can understand well enough to make this a solid learning opportunity to get my brainstorming working in other directions for similar sdk based agent opportunities using paid LLMs.. there is overlap with track1 here but that is totally fine and reinforces concepts in different ways.)


### COWORK

Fyi, I just finished the "learn-ai track restructure" via claude cli in my vscode/wsl/ubuntu/learn-ai local repo which I have committed to main and pushed to remote.
make sure to `git pull` if you found a way to clone this repo somewhere.

Remember that these track-02-free-tier modules dont have to only cover dev use cases in vscode/wsl/ubuntu... I also want to cover walking the user through each of those 4 provider's web
app interfaces (I know all 4 currently have various web app interfaces), and the mobile app options, and the windows pc app options, and the vscode dev options. all for free tier. 
it is actually very useful to call out when a provider does not have a particular offering available in one of those areas, I think we could put this in the track-02-free-tier/README.md
where a bullet list will list each provider, their offerings in web/mobile-app/pc-app/vscode-dev, modules for each as available or if not a note pointing out not available and why (if possible).
Note that later I will work with claude cli to create/update the `.claude/agents/freshness-auditor.md` agent to facilitate keeping this information up to date with the latest actual offerings reality.

Proceed with actual walkthrough to get antigravity cli installed. Note that I want to do this (helps get the info to stick in my brain), so walk me through it one step at a time.
You can use 'computer use' to browse the web pages as needed.
Ultimately this will need to be written up in one of the modules in track-02-free-tier.

https://antigravity.google/docs/overview & https://antigravity.google/docs/cli/overview currently are open in my chrome browser. 
Note that antigravity.google/docs/cli returns 404 "Error: Not Found" for me too.








### LATER (after implementing the base set of modules for track02)
TODO ask fable-max for a context based agent (I may already have one) that specializes in researching the latest state of ai platform offerings and alerting me via some
    intermediary file or item added to the TODO.md backlog with a link to a plan for updating this learn-ai repo so it is up to date with the latest offerings.
    This agent might be the final judge that confirms the learn-ai repo is up to date.
    `.claude/agents/freshness-auditor.md` is similar, should we update it or is this distinct enough to warrant a separate agent.
    Or, I also wonder if we should have a different freshness-auditor for each "Track"; like one that specializes in local hosted models, one that specializes in claude code offerings, one for openai offerings, one for github copilot, one for gemini.



