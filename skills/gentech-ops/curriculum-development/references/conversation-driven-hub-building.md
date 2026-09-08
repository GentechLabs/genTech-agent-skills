# Conversation-Driven Hub Building — Lynn Session (Jul 27, 2026)

## Student Profile
- **Name:** first pilot student (departed Aug 2026)
- **Background:** Non-technical mom, Lapu-Lapu Cebu, Cebuano primary
- **Hub file:** `10-Labs/gentech-academy/{name}-hub-template.html`
- **Vault path:** `/root/vaults/gentech/10-Labs/gentech-academy/{name}-hub-template.html`

## Sections Built (in order)

| # | Section | Student Provided | Agent Built |
|---|---------|-----------------|-------------|
| 1 | About Me | Personal story in her own words | Two styled paragraphs with her exact text |
| 2 | 🧳 My Travel Wishlist | 3 destinations + ₱ budgets + message | Budget cards (₱800/₱600/₱450/₱1,850 total) + photo cards with real images |
| 3 | 🍲 My Daily Meals | 2 recipes + costs + ingredients | Meal cards with ingredient tags, cost display, gradient headers |
| 4 | 🛍️ My Smart Finds | 3 items + prices + descriptions | Find cards with price tags, gradient icons, descriptions |

## Photo Handling
- Student shared 3 photos in chat (Oslob whale sharks, Kawasan Falls, Simala Shrine)
- Images saved to `/root/vaults/gentech/assets/{student}/`
- Embedded as base64 data URIs directly in the HTML (no external hosting needed)
- CSS: `object-fit:cover; height:180px` for consistent card image display

## CSS Patterns Used
- `.dream-grid` / `.dream-card` — travel wishlist cards
- `.meal-grid` / `.meal-card` — meal cards with `.meal-ingredients` tag pills
- `.finds-grid` / `.find-card` — shopping find cards
- All use same base pattern: `background:rgba(255,255,255,0.02)`, `border-radius:12px`, `hover:translateY(-2px)`
- Color-coded by category: travel=blue/green/purple, meals=red/green, shopping=pink/blue/yellow

## Sections Built (continued)

| # | Section | Student Provided | Agent Built |
|---|---------|-----------------|-------------|
| 5 | ⭐ My Wishlist | Washing machine, refrigerator, TV + ₱ ranges + "pangandoy" message | Wish cards with price ranges, savings plan (₱100/week → X months), gradient icons |
| 6 | ✈️ Things I Love | (pre-existing) | 3-tab interface: Travel, Shopping, Cooking |
| 7 | 📚 Academy Lessons | (pre-existing) | Progress tracker with status badges |

## Wishlist Section Pattern

The ⭐ My Wishlist section is distinct from 🛍️ Smart Finds:

| Aspect | Smart Finds | Wishlist |
|--------|-------------|----------|
| **Tone** | Practical, "I shop wisely" | Emotional, "Pangandoy nako" |
| **Items** | Small purchases (₱95-₱150) | Big purchases (₱3,500-₱6,000) |
| **Price display** | Single price | Price range (₱MIN - ₱MAX) |
| **Savings plan** | None | ₱X/week → Y-Z months |
| **Framing** | "Worth every peso" | "Para sa pamilya" |

**Key pattern:** The wishlist message should be in the student's native language and express the emotional reason behind the goal (e.g., "para dali ra manglaba, maka-stock og pagkaon, ug dili na mag-gawas-gawas kay naa koy mga anak").

## Price Research Pattern

When a student asks about prices of appliances/items:

1. **Search** — web_search for "pinakamurang [item] price Philippines 2026"
2. **Extract** — web_extract on top result URLs for specific prices
3. **Structure** — Present as a table with: Type, Brand, Size, Price
4. **Recommend** — Pick the cheapest option and explain why it fits their situation
5. **Offer to add** — Ask if they want it on their wishlist

**Price table format:**
```
| Type | Brand | Size | Price |
|------|-------|------|-------|
| [Type] | [Brand] | [Size] | ₱[MIN] - ₱[MAX] |
```

**Savings plan calculation:**
- ₱100/week → item price / 100 = weeks to save
- ₱200/week → item price / 200 = weeks to save
- Display as "₱X/week → makuha sa Y-Z months"

## Emotional Support Pattern

When a student shares a personal/emotional revelation (e.g., "I never experienced someone give me flowers"):

1. **Acknowledge the feeling** — validate without pity
2. **Affirm their worth** — "deserve mo yan"
3. **Offer to capture it** — "Pwede nating idagdag sa wishlist mo"
4. **Keep it light** — don't dwell, offer a constructive next step
5. **Use their native language** for warmth

## Key Techniques
- **Inline styles for unique elements** — budget cards and section descriptions use inline styles since they're one-off
- **CSS classes for repeated elements** — card grids use shared classes
- **Base64 image embedding** — photos from chat embedded directly, no external URLs needed
- **Section order** — personal (About Me) → dreams (Travel) → daily life (Meals) → practical (Shopping) → material goals (Wishlist) → fun (Things I Love tabs) → learning (Lessons)
- **Price ranges, not single prices** — for wishlist items, show a range (₱3,500-₱5,000) to account for brand/size variation
- **Savings plan** — always include a weekly savings projection so the goal feels achievable
- **Native language for emotional content** — Cebuano for "pangandoy" messages, English for technical descriptions
