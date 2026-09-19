# Two-Group Tool-Scout Handoff — write a tailored note per consumer

When a scouted tool helps MORE than one group, write a separate handoff for each
consumer — do not forward a single note. Each group has a different reason to care
and a different blocker the tool can fix.

## Proven Aug 22, 2026: 3D Generation Toolkit
- Routed to **Forge** (desktop/GPU lane): `labs-to-forge/2026-08-22-3d-generation-toolkit.md`
  — Hunyuan3D-2 (runnable WorldClaw code), TRELLIS, TripoSR, weigert/territory (agent
  voxel engine), threejson (MIT, web-native). Forge builds the 3D assets on the RTX 3070.
- Routed to **Pixel/Entertainment**: `labs-to-entertainment/2026-08-22-3d-generation-toolkit-pixel.md`
  — framed as the FIX for their #1 blocker (**character drift**). A 3D character mesh means
  every camera angle renders from the SAME geometry → face/outfit cannot drift → replaces
  their opacity-blend / CG-anchor / video-continuation workarounds. Also solves consistent
  3D environments for KAGE / Cold Crown.

## Method (generalize to any tool × group)
1. For each consuming group, read its latest EOD / `<group>-to-gentech` handoff to find
   its ACTIVE blocker.
2. Frame the tool as the fix for that SPECIFIC problem, with the mechanism (why it ends
   the pain), not just "here's a cool tool."
3. Name the executor (Forge) vs. the consumer (Entertainment) so each knows their role.
4. Include what gates it (funding, GPU, wallet) so the group doesn't over-commit.

A tool is a good find; a tool framed as "here's how it ends your #1 pain" is a handoff
that gets picked up.
