# Encoding vs Embedding

## Encoding
**Encoding** = converting data into numbers.

- Can be simple or fixed
- Does not always capture meaning

### Examples
- `"cat" → [1, 0, 0]`
- `"dog" → [0, 1, 0]`

---

## Embedding
**Embedding** = converting data into vectors that capture meaning.

- Learned by a model
- Similar meanings have similar vectors

### Examples
- `"king" → [0.2, 0.8, -0.1, ...]`
- `"queen" → [0.21, 0.79, -0.1, ...]`

---

## Difference

| Encoding | Embedding |
|---|---|
| Converts data to numbers | Converts data to meaningful vectors |
| Often fixed | Learned |
| No meaning required | Meaning is captured |

---

## One-line Summary
- **Encoding** = numbers
- **Embedding** = meaningful numbers
