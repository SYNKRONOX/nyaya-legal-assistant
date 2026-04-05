# IPC to BNS Section Mapping Reference

## ⚠️ CRITICAL: Section Numbers Have Changed!

The Bharatiya Nyaya Sanhita (BNS) 2023 has **completely reorganized** Indian criminal law. 
**Section numbers are NOT the same** between IPC and BNS!

## Common Examples of Different Section Numbers

| Crime | IPC Section | BNS Section | Notes |
|-------|------------|-------------|-------|
| **Murder** | **302** | **103** | Most famous example! |
| **Culpable Homicide** | 304 | 105 | |
| **Dowry Death** | 304B | 80 | |
| **Rape** | 376 | 63-70 | Multiple sections in BNS |
| **Theft** | 379 | 303 | |
| **Robbery** | 390 | 309 | |
| **Cheating** | 420 | 318 | Yes, "420" is gone! |
| **Sedition** | 124A | Removed | No longer a crime in BNS |

## How Your App Handles This

### 1. **Query Detection** (agents.py)
```python
# Detects which code the user is asking about
query = "What is Section 302?"
detected_code = detect_legal_code(query)  # Returns 'IPC', 'BNS', or 'BOTH'

# Default behavior: Assumes BNS for ambiguous queries
# (since it's the current law)
```

### 2. **Code Filtering** (retriever.py)
```python
# Only retrieves from the requested code
results = retriever.hybrid_search(
    query="Section 302", 
    code_filter='BNS'  # Only returns BNS sections
)
```

### 3. **Explicit Labeling** (all responses)
```
Your Answer: "BNS Section 103 deals with murder..."
NOT: "Section 103 deals with murder..."
```

## User Query Examples

### ✅ GOOD (Explicit)
- "What is **IPC** Section 302?"
- "Explain **BNS** Section 103"
- "Compare IPC 302 vs BNS 103"

### ⚠️ AMBIGUOUS (App defaults to BNS)
- "What is Section 302?" → **App will return BNS Section 302 (Snatching)**
- "Punishment for murder?" → App searches both, prioritizes BNS

### 🔍 COMPARISON (App returns both)
- "Difference between IPC and BNS for murder"
- "What changed from IPC 302 to BNS?"

## For Users: How to Ask Questions

1. **Be Specific**: Always mention IPC or BNS if you know which one
   - Good: "What is **IPC Section 302**?"
   - Bad: "What is Section 302?"

2. **Use Crime Names**: More reliable than section numbers
   - Good: "What is the punishment for **murder**?"
   - Good: "Explain the law on **theft**"

3. **Ask for Comparisons**: App handles this well
   - "How did BNS change the law on cheating?"
   - "What's the difference between IPC 420 and BNS 318?"

## Technical Implementation

### PDF Extraction (05_extract_from_pdf.py)
```python
# Each section is tagged with code
enriched_text = f"==== IPC (Indian Penal Code 1860) ====\n"
                f"IPC Section 302: Murder\n\n"
                f"[Legal Code: IPC, Section: 302]"
```

### Retrieval (retriever.py)
```python
def _filter_by_code(results, code_filter):
    # Filters results to only IPC or BNS
    if code_filter == 'IPC':
        return [r for r in results if 'IPC' in r['text'][:100]]
    elif code_filter == 'BNS':
        return [r for r in results if 'BNS' in r['text'][:100]]
```

### Response Generation (agents.py)
```python
prompt = f"""
IMPORTANT: The user is asking about {code_context}.

Instructions:
1. ALWAYS specify which legal code (IPC or BNS)
2. Format citations as: "IPC Section 302" or "BNS Section 103"
3. If ambiguous, clarify: "Did you mean IPC 302 or BNS 302?"
"""
```

## Comprehensive Section Mapping

*Note: This is a simplified mapping. The actual BNS has restructured many sections.*

### Offences Against the Human Body

| IPC Section | Crime | BNS Section |
|-------------|-------|-------------|
| 299-300 | Culpable Homicide | 101-102 |
| 302 | Murder | 103 |
| 304 | Culpable Homicide not Murder | 105 |
| 304A | Death by Negligence | 106 |
| 304B | Dowry Death | 80 |
| 307 | Attempt to Murder | 109 |
| 323 | Simple Hurt | 115 |
| 325 | Grievous Hurt | 117 |

### Sexual Offences

| IPC Section | Crime | BNS Section |
|-------------|-------|-------------|
| 375-376 | Rape | 63-70 |
| 376A | Man causing death of woman | 64(2) |
| 376D | Gang Rape | 70 |
| 354 | Assault on woman | 74 |
| 509 | Word/gesture to insult modesty | 79 |

### Offences Against Property

| IPC Section | Crime | BNS Section |
|-------------|-------|-------------|
| 378 | Theft | 303 |
| 379 | Punishment for Theft | 303 |
| 380 | Theft in dwelling | 304 |
| 390 | Robbery | 309 |
| 392 | Punishment for Robbery | 309 |
| 420 | Cheating | 318 |
| 425 | Mischief | 324 |

### Public Order Offences

| IPC Section | Crime | BNS Section |
|-------------|-------|-------------|
| 141-149 | Unlawful Assembly | 189-191 |
| 153A | Promoting enmity | 196 |
| 295A | Insulting religion | 299 |
| 505 | Public mischief | 196 |

### Offences Against the State

| IPC Section | Crime | BNS Section |
|-------------|-------|-------------|
| 121 | Waging war | 147 |
| 121A | Conspiracy to wage war | 147 |
| 124A | Sedition | **REMOVED** |
| 125 | Waging war against Asian power | 148 |

## Important Notes

1. **BNS is the current law** (2023 onwards)
2. **IPC is legacy** but still referenced
3. **Many section numbers changed** - don't assume!
4. **Some crimes removed** (e.g., Sedition)
5. **Some crimes added** (e.g., organized crime provisions)

## Testing Your App

Try these queries to test code disambiguation:

```
1. "What is Section 302?" 
   → Should return BNS 302 (Snatching) with clarification about IPC

2. "What is IPC Section 302?"
   → Should return IPC 302 (Murder) ONLY

3. "Compare IPC 302 and BNS 103"
   → Should show both with differences

4. "Punishment for murder in India"
   → Should return BNS 103 (current law)
```

## Summary

✅ **Your app NOW handles IPC/BNS disambiguation correctly:**
- Detects which code from query
- Filters results by code
- Labels all citations clearly
- Defaults to BNS (current law)
- Supports comparison queries

❌ **Without this fix, your app would:**
- Mix up IPC 302 (Murder) with BNS 302 (Snatching)
- Give outdated IPC information for current law questions
- Confuse users with ambiguous citations

