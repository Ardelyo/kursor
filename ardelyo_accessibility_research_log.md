# Ardelyo's Accessibility Research Log - Face/Hand Mouse Tracker

## May 1, 2025
**Theme:** Project Inception & Initial Goals
- So excited to finally kick off this face/hand mouse tracker project! I truly believe this could be a game-changer for individuals who find traditional mice difficult or impossible to use. The potential to unlock digital access is immense.
- My core accessibility principles for this project are:
    1.  **Strive for WCAG AA compliance:** Even though it's a hardware/software interface, the principles apply, especially to the settings UI.
    2.  **Prioritize customization:** Users *must* be able to tailor the experience to their specific needs and abilities. One size will not fit all.
    3.  **Design for diverse abilities:** Consider users with tremors, limited range of motion, fatigue, and varying levels of tech-savviness.
    4.  **Intuitive Interaction:** The gestures and controls should feel as natural and require as little cognitive load as possible.
- The biggest challenge I foresee is balancing sensitivity with stability – making it responsive without being overly jittery or fatiguing to use for extended periods. How do I make this intuitive and not tiring? That's the million-dollar question.

## May 2, 2025
**Theme:** Basic Tracking & Pointer Control
- Got the first basic prototype for cursor movement up and running today! Hooked up the camera, and I can now move the pointer using gross head movements and also by tracking my hand. It's a bit jittery, especially with head tracking, but it's a start!
- Early observation: Hand tracking seems more precise for fine-tuned movements, while broader face gestures might be better for sweeping cursor movements across the screen. Need to investigate this further.
- Definitely need robust sensitivity adjustments. I'm thinking sliders for X/Y sensitivity, maybe some presets for common scenarios like "High Precision" (dampened) vs. "Quick Move" (more reactive). Also, how to filter out tremors effectively without losing intentional micro-movements?
- A big consideration for tomorrow: How will users initially calibrate this? The first-run experience needs to be super simple and guided. Maybe a wizard that helps them define their neutral position and movement boundaries.

## May 3, 2025
**Theme:** Click Mechanisms - Part 1 (Dwell Click)
- Dove into dwell click research today. It seems like a solid foundational clicking mechanism for users who can position the cursor accurately but might struggle with a physical click action.
- Key design considerations for dwell click:
    -   **Adjustable Dwell Time:** This is critical. Users need to set this from very short to quite long.
    -   **Clear Visual Feedback:** I'm thinking of a circular progress bar that fills up around the cursor, or maybe the cursor icon itself changes. This feedback needs to be unambiguous.
    -   **Auditory Feedback (Optional):** A subtle sound cue when the dwell click registers could be helpful for some.
- Started coding the dwell click module. The main challenge is making the dwell timer easily configurable and ensuring the visual feedback is smooth and not distracting.
- A potential issue I need to address early on is preventing accidental dwell clicks. Maybe a slight 'escape' movement of the cursor could cancel the dwell timer if it's still in progress.

## May 4, 2025
**Theme:** Click Mechanisms - Part 2 (Gesture-based Click)
- Spent today brainstorming and sketching out ideas for gesture-based clicks. The goal is simple, distinct, and non-fatiguing gestures.
- Some initial thoughts for gestures:
    -   **Face:** Small smile, quick eyebrow raise, cheek twitch, maybe even a specific mouth shape (like 'ooh').
    -   **Hand:** Quick hand clench/release, finger tap (if tracking individual fingers), or a small wrist flick.
- Mis-clicks are a major concern. How do I differentiate between a deliberate click gesture and an accidental facial expression or hand movement? Maybe a "gesture confirmation" mode where the system indicates it detected a potential click and awaits a tiny confirming movement or a brief pause.
- I'm also thinking about how to handle different click types. Perhaps a smile for a left click and an eyebrow raise for a right click? Or use a modifier system, like a specific sustained expression to switch to 'right-click mode'.
- Sketched out a few gesture ideas on paper and tried to act them out. Need to actually test which ones are most reliably picked up by the current tracking library without being too sensitive to normal expressions or movements. This will require a lot of trial and error.

## May 5, 2025
**Theme:** User Profiles & Customization
- It's becoming abundantly clear that users will have vastly different needs and preferences. A one-size-fits-all approach won't work. So, user profiles are a must!
- What settings should these profiles save? Pretty much everything:
    -   Pointer sensitivity (X/Y axes, smoothing).
    -   Dwell click settings (time, visual/auditory feedback).
    -   Selected click gestures (and their individual sensitivity/thresholds).
    -   Calibration data (neutral position, movement range).
    -   UI preferences for the settings panel (font size, contrast theme).
- The accessibility of the settings interface itself is paramount. If users can't configure the tool, it's useless. This means the settings panel must be navigable using the face/hand tracker itself (a fun challenge!) or, at the very least, be fully keyboard accessible (Tab, Enter, Arrow keys, etc.).
- Must ensure good color contrast and legible font sizes in the settings UI, adhering to WCAG AA at a minimum.
- Began outlining the data structure for user profiles today. Thinking about JSON for easy storage and retrieval. This will be foundational for making the tool truly adaptable.

## May 6, 2025
**Theme:** Addressing User Fatigue
- Realized today that using face/hand tracking for extended periods can definitely be tiring. Constant, precise movements are demanding. I need to build in ways to mitigate this.
- My main idea is a 'pause' gesture. Maybe closing eyes for two seconds, or holding a specific hand sign, could temporarily disable tracking. This would allow users to relax, readjust, or talk without the cursor flying around.
- Also spent a lot of time exploring smoothing algorithms. The goal is to dampen minor involuntary movements, like tremors, making pointer control less of a fight. I've got a basic Kalman filter implemented, and it seems to help, but it's a delicate balance. Need to balance responsiveness with aggressive smoothing – too much smoothing feels laggy and unresponsive. This will need to be a configurable setting.

## May 7, 2025
**Theme:** Software UI/UX - Initial Thoughts
- Started sketching out mockups for the control panel UI today. My mantra is: clarity, simplicity, and large clickable targets. No tiny buttons or confusing layouts!
- Given the user base, I'm prioritizing making the settings panel itself highly accessible. This means full keyboard navigation is non-negotiable. I've been mapping out the tab order for all controls and ensuring that every interactive element can be activated using Space or Enter.
- If the user can't easily change settings, the customizability is lost. The settings panel itself must be accessible. I'm also thinking about high-contrast themes and font size options directly within the panel.

## May 8, 2025
**Theme:** Screen Reader Compatibility for Software
- Today was all about screen reader compatibility for the settings application. If it ends up being a web-based UI, I'll need to use semantic HTML and ARIA attributes diligently. For a desktop app, I'll need to leverage the platform's accessibility APIs.
- Did some initial tests with NVDA on a prototype of the settings panel. It was a bit of a wake-up call! Some buttons were unlabelled, and the reading order was a bit confusing. Definitely need to add `aria-label` for icon-only buttons and `aria-describedby` for providing extra hints on complex settings.
- Realized how crucial it is to test with actual screen readers regularly, not just assume it'll work. Small changes can have a big impact on screen reader usability.

## May 9, 2025
**Theme:** Documentation - Part 1 (Beginner's Guide)
- Started outlining the "Quick Start" guide today. It needs to be incredibly clear and simple, using plain language and step-by-step instructions. I'm picturing lots of screenshots.
- I'm also seriously considering creating short, focused video tutorials for key tasks: initial setup, camera positioning, gesture calibration, and basic use. Visuals can be so much more effective for some users.
- A critical point for videos: they *must* have accurate, synchronized captions. And ideally, audio descriptions for users who are visually impaired and can't see the screen content clearly. Accessibility has to extend to the support materials too!

## May 10, 2025
**Theme:** Testing with Simulators/Emulators
- Spent some time today exploring tools and browser extensions that simulate various disability conditions – things like low vision (blur, contrast loss), color blindness, and even some motor impairment simulators that make mouse control more difficult.
- Used these to do a first pass on the settings UI and the draft documentation. It's surprising how quickly you can spot issues, like poor contrast on a button when viewed through a "low vision" filter.
- Of course, I know that simulators are no substitute for testing with real users who live with these conditions daily. But they can definitely help catch some of the more obvious design flaws early in the process, before I get too far down a particular path. It’s a good sanity check.

## May 11, 2025
**Theme:** Refining Gesture Recognition
- Back to gesture recognition today. The current smile detection is a bit too sensitive – it sometimes triggers when I'm just talking or making a slight facial expression! Need to work on the thresholds and perhaps add some temporal filtering (gesture must be held for X milliseconds).
- The big idea I started implementing is a calibration mode for gestures. Instead of relying on a generic model for a "smile" or "hand clench," users will be able to "teach" the system their unique way of performing these gestures. This should significantly improve accuracy and reduce false positives.
- This calibration process itself needs to be accessible, of course. Clear instructions, good feedback.

## May 12, 2025
**Theme:** Advanced Pointer Control (Beyond Basic Movement)
- Brainstorming advanced pointer control today. Basic movement and clicking are essential, but users need scrolling, dragging, and right-clicking too.
- For scrolling, I'm considering a "scroll mode" activated by a gesture (e.g., puffed cheeks). Once in scroll mode, slight upward/downward head tilts or small vertical hand movements could control scroll speed and direction.
- Dragging and dropping could be a "click and hold" gesture (maybe a longer version of the standard click gesture), then move the cursor, then a "release" gesture (perhaps just relaxing the initial click gesture).
- For right-click and other click types, I could use a distinct gesture (e.g., eyebrow raise for right-click if smile is left-click), or a modifier gesture that cycles through click types (left, right, double, drag-lock) before the main click gesture is performed.
- Mapping these more complex actions to intuitive and non-fatiguing face/hand movements is tricky. They need to be easily discoverable and not overly complex to remember or perform. This will require careful design and lots of user testing.

## May 13, 2025
**Theme:** Accessibility for Setup & Calibration
- Focused heavily on the accessibility of the initial setup and calibration process today. The first experience a user has with the software is crucial. If calibration is frustrating or impossible for them, they might give up before even trying the core functionality.
- If there's a visual calibration step, like asking the user to look at the corners of the screen, I need to think about non-visual alternatives or aids. Perhaps a series of auditory cues that guide them?
- I'm seriously considering voice-guided setup options. The system could speak instructions clearly ("Please look at the center of your screen and hold still") and provide spoken feedback ("Neutral position calibrated successfully"). This would be a huge win for users with visual impairments or those who have difficulty reading on-screen text.

## May 14, 2025
**Theme:** Documentation - Part 2 (Advanced Features & Troubleshooting)
- With more features getting prototyped, it's time to think about the next layer of documentation: advanced features and troubleshooting.
- I started drafting an FAQ section to address common issues I anticipate, like "What if tracking is jittery?", "My click gesture isn't recognized consistently?", or "How do I adjust sensitivity for fine motor control?".
- It's also important to provide clear explanations of how different settings interact. For example, how smoothing affects sensitivity, or how dwell click settings might need to change if gesture clicking is also enabled.
- I think a dedicated section on "Tips for Users with Tremors" or "Maximizing Comfort During Extended Use" would be invaluable, offering practical advice for specific user needs.

## May 15, 2025
**Theme:** Gathering User Feedback - Planning
- Today was less about coding and more about planning for a crucial phase: gathering user feedback. This project is for users with disabilities, and their input is paramount.
- I'm researching strategies to connect with potential testers: reaching out to online accessibility forums, contacting disability advocacy groups, and perhaps connecting with local community centers or assistive technology resource centers.
- I started designing feedback forms and questionnaires. I need to ask specific questions about usability, physical and cognitive fatigue, the intuitiveness of gestures, and any features they feel are missing or could be improved. Open-ended questions will be important too.
- Ethical considerations are top of mind: ensuring all interactions are respectful, that data is handled privately and securely, and that participants understand how their feedback will be used. Real user feedback will be the most valuable input for the next iteration of this project.

## May 16, 2025
**Theme:** Considering Different Operating Systems
- Thinking about cross-platform compatibility today. If the software component that handles tracking and settings is a desktop application, I need to consider how it will run on Windows, macOS, and Linux.
- Each OS has its own nuances for camera access, input control, and accessibility APIs. For instance, UI elements might look and behave slightly differently, and screen reader interactions could vary.
- My goal is to provide a consistent core experience, even if there are minor OS-specific adjustments. This means I'll need to set up test environments for each OS eventually. I'll start with Windows as it's the largest user base, but I don't want to exclude Mac or Linux users if I can help it.

## May 17, 2025
**Theme:** Exploring Broader Applications
- Stepped back from the core mouse control features today to brainstorm broader applications. If I can provide a reliable and nuanced hands-free input stream, where else could it be used?
- **Gaming:** Could this be used for hands-free game controls? Perhaps for simpler games, or specific in-game actions. Accessibility in gaming is a big field.
- **Communication aids:** Integration with on-screen keyboards or specialized communication software could be powerful for users who can't type or speak easily. A reliable head pointer or gesture click could make a world of difference.
- **Art/Music creation:** Could face or hand gestures control brush strokes in a painting program, trigger notes or effects in music software, or manipulate 3D models?
- The potential is huge if I can make the input robust and customizable enough. It's inspiring to think beyond just replacing the mouse.

## May 18, 2025
**Theme:** Integration with Other Assistive Technologies
- Following on from yesterday's brainstorming, I thought about how this face/hand tracker could integrate with *other* assistive technologies. The goal is to expand options for users, not necessarily replace other AT they find useful.
- For example, a user might primarily use switch access for certain tasks but prefer face/hand tracking for finer pointer control or specific gestures. The two systems should be able to coexist.
- Could it provide a complementary input to eye gaze systems? Perhaps for users who have some head/hand movement but not enough consistent control for eye gaze alone, or for whom eye gaze is fatiguing.
- The key is flexibility and ensuring the software doesn't monopolize input devices in a way that prevents other AT from functioning.

## May 19, 2025
**Theme:** Finalizing Core Features & UI
- Coming towards the end of this initial 20-day development sprint. Today, I did a thorough review of all the core features I've prototyped – pointer movement, dwell click, gesture clicking, and the settings panel – against my initial accessibility goals.
- I specifically focused on the settings panel UI again. Did a quick pass with NVDA and VoiceOver (on a Mac VM). Much better than my first test! Most labels are now correct, and tab order is logical. Still a few minor tweaks needed for ARIA roles on some custom controls I built.
- I also started creating a checklist based on WCAG principles (Perceivable, Operable, Understandable, Robust) and tried to map my features and UI design choices to them. For example, 'Adjustable dwell time' maps to Operable (Enough Time), and 'Clear visual feedback for dwell' maps to Perceivable. It's a good way to self-assess and spot gaps.

## May 20, 2025
**Theme:** Project "Alpha" Completion & Next Steps
- And that's a wrap for the initial 20-day "Alpha" sprint! It's been intense, but I'm pretty happy with the foundation that's been laid.
- **Achievements:**
    - Basic face and hand tracking for cursor movement is functional.
    - Dwell click mechanism is implemented with adjustable timing and visual feedback.
    - Initial framework for gesture-based clicking is in place (though needs refinement and robust calibration).
    - User profiles for saving settings are designed.
    - The settings UI has been designed with accessibility as a core principle (keyboard navigation, considerations for screen readers).
    - Initial documentation and plans for user feedback are outlined.
- **Key Learnings:** Balancing sensitivity and stability is the biggest technical challenge. User customizability is paramount. Accessibility must be baked in from day one, not bolted on.
- **Known Limitations:** Gesture recognition is still rudimentary. Fatigue management needs more robust solutions. Cross-OS testing is minimal so far.
- **Next Steps:** The absolute priority is structured user testing with a diverse group of users with different abilities. Their feedback will drive the next phase of development. After that, it's refining algorithms, adding more reliable gestures based on feedback, and iteratively improving the settings UI and overall user experience.
- This 20-day sprint has laid a strong foundation. The real work of iteration based on user needs starts now! I'm excited for what's next.
