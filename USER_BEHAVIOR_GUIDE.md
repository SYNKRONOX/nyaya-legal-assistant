# 👥 Nyaya Legal Assistant - User Behavior Guide

## 📅 CRITICAL LEGAL CONTEXT

**July 1, 2024**: Indian Penal Code (IPC 1860) was **OFFICIALLY REPEALED**  
**Current Law**: Bharatiya Nyaya Sanhita (BNS 2023) is the law of the land

---

## 🎯 How Your App Behaves for Different Users

### 1️⃣ **General Public** (Default)

**Intent**: Current law applicable in 2026

| User Query | App Response |
|------------|--------------|
| "What is the punishment for murder?" | **BNS Section 103**: Punishment is... (NO IPC mentioned) |
| "Is cheating a crime?" | **BNS Section 318** covers cheating... (NO IPC) |
| "What is Section 302?" | **BNS Section 302** (Snatching). *Note: If you meant IPC, it was repealed July 2024.* |

✅ **Behavior**: BNS ONLY (IPC not mentioned)  
✅ **Reasoning**: General public needs current law, not history  
✅ **Format**: "Under BNS Section XXX..."

---

### 2️⃣ **Law Students / Legal Professionals**

**Intent**: Educational understanding + historical context

| User Query | App Response |
|------------|--------------|
| "Explain the law on murder" | **Current law (BNS 103)**: Punishment is...<br>**Previously (IPC 302)**: Was punished by... |
| "Compare IPC and BNS on theft" | **IPC 379** (repealed): Defined theft as...<br>**BNS 303** (current): Now defines... |
| "Study difference in cheating laws" | **BNS 318** replaced **IPC 420**. Changes: 1) ... 2) ... |

✅ **Behavior**: BNS primary + IPC for educational context  
✅ **Reasoning**: Law students need to understand evolution  
✅ **Format**: "Current law (BNS)... Previously (IPC)..."

---

### 3️⃣ **Explicit IPC Query** (Historical)

**Intent**: User specifically asking about old law

| User Query | App Response |
|------------|--------------|
| "What was IPC Section 302?" | **IPC Section 302** (REPEALED July 1, 2024): Murder...<br>⚠️ **For current law, see BNS Section 103** |
| "Explain IPC 420" | **IPC Section 420** (REPEALED): Cheating...<br>⚠️ **Replaced by BNS Section 318** |

✅ **Behavior**: Shows IPC with CLEAR repeal warning  
✅ **Reasoning**: Historical research or comparison  
✅ **Format**: "IPC XXX (REPEALED July 2024)... Current: BNS YYY"

---

### 4️⃣ **Comparison Query** (Side-by-side)

**Intent**: Understand what changed from IPC to BNS

| User Query | App Response |
|------------|--------------|
| "Compare IPC 302 vs BNS 103" | **IPC 302** (repealed): Murder, punishment...<br>**BNS 103** (current): Murder, punishment...<br>**Changes**: 1) ... 2) ... |
| "Difference between IPC and BNS for rape" | **IPC 376** (repealed) vs **BNS 63-70** (current)<br>Key changes: Expanded provisions for... |

✅ **Behavior**: Shows both codes side-by-side  
✅ **Reasoning**: Understanding legal evolution  
✅ **Format**: "IPC XXX (repealed) vs BNS YYY (current)"

---

## 🔍 Detection Logic (How App Decides)

```
User Query → Intent Detection → Code Selection → Response Style
```

### Intent Detection Triggers

| Intent | Detection Keywords | Code Retrieved | Response Style |
|--------|-------------------|----------------|----------------|
| **current_law** | (default, no IPC mention) | BNS only | BNS only, no IPC |
| **historical** | "IPC", "was", "old law" | IPC only | IPC + repeal notice |
| **comparison** | "compare", "difference", "vs", "changed" | Both | Side-by-side |
| **law_student** | "study", "learn", "explain both", "understand" | Both | Educational format |

---

## 📊 Examples by User Type

### General Public (2026 queries)

```
❓ "Can I be jailed for theft?"
✅ "Yes, under BNS Section 303, theft is punishable by..."
   (No IPC mention - it's irrelevant for 2026 crimes)

❓ "What is Section 420?"
✅ "BNS Section 420 is... Note: If you meant the famous IPC 420 
   (cheating), it's now BNS Section 318."
   (Clarification but focuses on current law)
```

### Law Students

```
❓ "Explain the law on murder"
✅ "Under current law (BNS Section 103), murder is defined as...
   
   Previously, IPC Section 302 defined murder as... 
   
   Key changes in BNS:
   1) ...
   2) ..."
   (Educational: shows evolution)

❓ "Study provisions for sexual offences"
✅ "Current law (BNS 2023):
   - BNS Sections 63-70 cover sexual offences
   
   Historical context (IPC 1860, repealed 2024):
   - IPC Section 376 and related provisions
   
   Evolution: BNS expanded protections by..."
   (Comprehensive learning context)
```

### Legal Researchers

```
❓ "What was IPC Section 124A?"
✅ "IPC Section 124A (SEDITION) was repealed July 1, 2024.
   This provision has been REMOVED in BNS - sedition is no 
   longer a crime under Indian law."
   (Historical accuracy + current status)

❓ "Compare IPC 302 and BNS 103"
✅ "IPC Section 302 (Murder) - REPEALED July 2024:
   - Definition: [...]
   - Punishment: Death or life imprisonment
   
   BNS Section 103 (Murder) - CURRENT LAW:
   - Definition: [...]
   - Punishment: Death or life imprisonment
   
   Key differences:
   1) Section number changed
   2) [Any substantive changes]"
   (Academic comparison)
```

---

## 🚀 Technical Implementation

### Query Flow

```
1. User asks: "What is the punishment for theft?"
   ↓
2. Intent Detection: "current_law" (no IPC mention)
   ↓
3. Code Selection: BNS only
   ↓
4. Retrieval: Fetch BNS Section 303 (not IPC 379)
   ↓
5. Response: "Under BNS Section 303, theft is punishable by..."
   (No IPC mentioned)
```

### Safety Features

✅ **Default to BNS**: Unless explicitly requesting IPC  
✅ **Clear repeal warnings**: When showing IPC  
✅ **Date awareness**: "As of July 1, 2024..."  
✅ **No confusion**: Never mix codes without labeling  
✅ **Educational value**: Law students get both when helpful

---

## 🎓 Recommendations for Users

### General Public
✅ **DO**: Ask about crimes/punishments without code names  
✅ **DO**: "What is the punishment for X?"  
❌ **DON'T**: Worry about IPC vs BNS - app handles it

### Law Students
✅ **DO**: Ask for comparisons ("Compare IPC and BNS on X")  
✅ **DO**: Use keywords like "explain both", "study"  
✅ **DO**: Request historical context when needed

### Legal Professionals
✅ **DO**: Be specific about which code (if you need IPC)  
✅ **DO**: Ask for evolution/changes for research  
✅ **DO**: Request side-by-side comparisons

---

## 📌 Summary

| User Type | Default Behavior | IPC Shown? | Format |
|-----------|-----------------|------------|--------|
| **General Public** | BNS only | ❌ No | Current law only |
| **Law Students** | BNS + IPC | ✅ Yes (educational) | BNS → IPC context |
| **Explicit IPC Query** | IPC + warning | ✅ Yes (historical) | IPC (REPEALED) + BNS |
| **Comparison** | Both codes | ✅ Yes (analytical) | Side-by-side |

---

## 🏆 Result

✅ General public gets **accurate, current law** (BNS)  
✅ Law students get **educational context** (BNS + IPC)  
✅ Historical queries get **clear repeal warnings**  
✅ Comparison queries get **detailed analysis**

**No confusion. No outdated law. Context-aware responses.** 🎯

