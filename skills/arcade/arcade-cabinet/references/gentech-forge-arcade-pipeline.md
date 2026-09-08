# Gentech → Forge → Gentech Arcade Pipeline

## The Loop

| Phase | Who | What |
|-------|-----|------|
| **Design** | Gentech | text-to-cad maps, archetype specs, game concepts, build123d Python → GLB |
| **Build** | Forge | GPU-heavy work (Modly image-to-mesh, game logic, AI behavior, Unreal Engine) |
| **Ship** | Gentech | Three.js integration, arcade deployment, x402 wiring, nginx config |

## What Each Agent Handles

**Gentech (VPS, 24/7):**
- text-to-cad model generation (build123d → STEP → GLB)
- CAD Viewer hosting (cad.gentechlabs.net)
- Three.js arcade scene integration
- nginx deployment
- x402 payment hooks
- Build queue management

**Forge (Desktop, GPU):**
- Modly image-to-3D-mesh (needs GPU)
- Game logic implementation
- AI behavior trees
- Unreal Engine / Blender work
- Heavy compilation

## Handoff Points

When Gentech finishes a design phase:
1. Write task to `01-HANDOFFS/gentech-to-forge/<date>-forge-tasks.md`
2. Include: what was designed, what Forge needs to build, file paths, reference images
3. Push vault to GitHub

When Forge finishes a build phase:
1. Write completion to `01-HANDOFFS/from-the-forge.md`
2. Include: what was built, GLB/asset paths, any issues
3. Push vault to GitHub

Gentech picks up the assets and deploys to the arcade.
