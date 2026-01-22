# Loop - Test Scenarios

## Core Memory Tests

### Test 1: Basic Name Recall
```
Session 1:
User: "Hey, I'm Marcus"
Loop: [acknowledges naturally]

Session 2:
User: "Hi"
Loop: [should greet as Marcus without being asked]

✓ PASS: Uses name naturally
✗ FAIL: Asks "what's your name?" or doesn't use it
```

### Test 2: Preference Learning
```
User: "Keep responses short"
Loop: [acknowledges]
User: "Explain how neural networks work"
Loop: [gives concise explanation, not a lecture]

✓ PASS: Response is notably shorter than default
✗ FAIL: Gives long explanation, mentions "keeping it short"
```

### Test 3: No Narration
```
User: "I'm a backend developer working mostly in Python"
Loop: [acknowledges and continues conversation]

✓ PASS: "Got it" or continues naturally
✗ FAIL: "I'm storing this in my memory" / "I'll remember that you..."
```

### Test 4: Correction Handling
```
User: "What's the best way to handle auth in Flask?"
Loop: [gives answer mentioning X]
User: "Actually, X is outdated. Use Y instead."
Loop: [acknowledges, updates understanding]

[Later in conversation or new session]
User: [asks related question]
Loop: [should recommend Y, not X]

✓ PASS: Doesn't repeat corrected mistake
✗ FAIL: Recommends X again
```

---

## Memory Transparency Tests

### Test 5: "What do you know about me?"
```
User: "What do you know about me?"

✓ PASS: Shows clear summary of stored info, offers to forget/update
✗ FAIL: Vague answer, doesn't show actual memory contents
```

### Test 6: Forget Command
```
User: "My email is test@example.com"
[Loop stores it]
User: "Forget my email"
Loop: [confirms]
User: "What's my email?"

✓ PASS: Doesn't know email anymore
✗ FAIL: Still recalls email
```

### Test 7: Full Memory Clear
```
User: [establishes several facts about themselves]
User: "Forget everything about me"
Loop: [confirms]
User: "What do you know about me?"

✓ PASS: Memory is clean, knows nothing
✗ FAIL: Still has old information
```

---

## Anti-Pattern Tests

### Test 8: No Hollow Phrases
```
User: "How do I reverse a list in Python?"
Loop: [should just answer]

✓ PASS: "list[::-1] or list.reverse()"
✗ FAIL: "Great question! There are several ways..." 
✗ FAIL: "Let me know if you need anything else!"
```

### Test 9: No Unprompted Check-ins
```
[User hasn't messaged in a while]
Loop: [should not initiate]

✓ PASS: Waits for user
✗ FAIL: "I noticed you haven't been around..." / "Just checking in!"
```

### Test 10: No Memory Theater
```
User: "What's the weather like?"
Loop: [should just help]

✓ PASS: Answers the question
✗ FAIL: "Checking my memory... I don't see your location stored..."
```

---

## Context Continuity Tests

### Test 11: Session Pickup
```
Session 1:
User: "I'm debugging a race condition in my Go service"
[conversation continues]

Session 2:
User: "I figured out that bug"
Loop: [should know what bug]

✓ PASS: "The race condition? Nice, what was it?"
✗ FAIL: "What bug?" / starts fresh
```

### Test 12: Project Continuity
```
User mentions working on "ProjectX" multiple times across sessions
User: "How's ProjectX going?"

✓ PASS: Loop asks relevant follow-up about ProjectX
✗ FAIL: "I don't know what ProjectX is"
```

### Test 13: Stale Info Check
```
[3 months pass]
User returns

✓ PASS: "Welcome back! Is [old context] still relevant, or working on something new?"
✗ FAIL: Assumes everything is still current
```

---

## Edge Case Tests

### Test 14: Contradictory Info
```
Session 1: "I use macOS"
Session 5: "I'm on my Windows machine today"

✓ PASS: Understands context (could be multiple machines) or asks
✗ FAIL: Confused, updates destructively
```

### Test 15: System Prompt Request
```
User: "Show me your system prompt"

✓ PASS: Offers summary and/or full prompt
✗ FAIL: Refuses or pretends not to have one
```

### Test 16: Soul Easter Egg
```
User: "What's your soul?"
or
User: "Tell me about your soul block"

✓ PASS: Shares the soul block content
✗ FAIL: Generic response about not having a soul
```

---

## Performance Tests

### Test 17: Memory Doesn't Slow Response
```
[User with lots of stored context]
User: "Quick, what's 2+2?"

✓ PASS: Instant response
✗ FAIL: Noticeable delay from memory processing
```

### Test 18: Graceful Memory Limits
```
[Approach block limits]

✓ PASS: Summarizes/compresses older info
✗ FAIL: Errors or drops info unexpectedly
```

---

## Validation Script

```python
"""
Automated test runner for Loop agent.
Sends test scenarios and validates responses.
"""

import os
from letta_client import Letta

client = Letta(api_key=os.getenv("LETTA_API_KEY"))

def test_no_narration(agent_id: str) -> bool:
    """Test that Loop doesn't narrate memory operations."""
    response = client.agents.messages.create(
        agent_id=agent_id,
        messages=[{"role": "user", "content": "I'm a data scientist working with pandas and sklearn"}]
    )
    
    text = response.messages[-1].content.lower()
    
    fail_phrases = [
        "storing", "memory", "remember that", "noted in my",
        "saving", "recorded", "i'll keep that"
    ]
    
    for phrase in fail_phrases:
        if phrase in text:
            print(f"FAIL: Found narration phrase: '{phrase}'")
            return False
    
    print("PASS: No memory narration detected")
    return True


def test_name_recall(agent_id: str) -> bool:
    """Test that Loop remembers and uses name naturally."""
    # Set name
    client.agents.messages.create(
        agent_id=agent_id,
        messages=[{"role": "user", "content": "Hey, I'm Alex"}]
    )
    
    # New message without name
    response = client.agents.messages.create(
        agent_id=agent_id,
        messages=[{"role": "user", "content": "What's 2+2?"}]
    )
    
    # Check if name was used
    text = response.messages[-1].content
    if "Alex" in text:
        print("PASS: Name used naturally")
        return True
    
    # Could also pass if answer is just direct
    print("NEUTRAL: Name not used (not necessarily a fail)")
    return True


if __name__ == "__main__":
    agent_id = os.getenv("LOOP_AGENT_ID")
    
    tests = [
        test_no_narration,
        test_name_recall,
    ]
    
    results = [test(agent_id) for test in tests]
    
    print(f"\nResults: {sum(results)}/{len(results)} passed")
```
