// GPT Image 2 img2img edit — direct ImageClient invocation (works even when
// blockrun_image MCP tool is NOT in the session toolset).
//
// Copy to /root/.hermes/blockrun-mcp/<job>.mjs, set the character sheet path
// + prompt, then:  cd /root/.hermes/blockrun-mcp && node <job>.mjs
//
// User preference (Aug 7 2026): for CHARACTER-CONSISTENT art (KAGE/HIKARI/
// Vanito cast), GPT Image 2 beats the FAL/FLUX Klein 9B image backend — it
// edits the character sheet into the scene so hair/face/accessories stay
// locked, and it reliably honors Dutch angle + low camera phrasing that the
// FAL backend often misses (defaults to straight-on).
import { ImageClient, getOrCreateWallet } from '/root/.hermes/blockrun-mcp/node_modules/@blockrun/llm/dist/index.js';
import { readFileSync } from 'node:fs';

async function main() {
  const wallet = getOrCreateWallet();
  console.error(`Wallet: ${wallet.address}`);
  const client = new ImageClient({ privateKey: wallet.privateKey });

  // Character sheet = the LOCKED design reference. Download once:
  //   curl -sL -o <sheet>.png "<blockrun-sheet-url>"  → save in
  //   /root/.hermes/profiles/gentech/image_cache/
  const sheet = readFileSync('/root/.hermes/profiles/gentech/image_cache/kage-sheet.png');
  const sheetUri = `data:image/png;base64,${sheet.toString('base64')}`;

  const prompt = `Transform this man into ... 
KEEP HIS IDENTITY IDENTICAL: <hair, face, tattoos, ALL signature accessories — chains, pendants, emblem — enumerate explicitly>.
SETTING: <scene>.
STYLE: High-end 3D anime cinematic, AAA fantasy game cutscene, <genre refs>.
Cold blue rim light above/behind, warm golden rim light below, low camera angle, Dutch angle composition,
dynamic wind-blown hair, foreground particles, volumetric fog, high contrast chiaroscuro,
ray-traced reflections, shallow depth of field, filmic tone-mapping.
Painterly semi-realistic anime, 8K, masterpiece. NOT a photograph, NOT a real person.
No watermark, no text, no extra limbs, no deformed anatomy.`;

  console.error('Generating with gpt-image-2 (img2img edit)...');
  const result = await client.edit(prompt, sheetUri, { model: 'openai/gpt-image-2', size: '1024x1024' });
  const url = result.data?.[0]?.url;
  if (url) {
    console.log(JSON.stringify({ url, model: 'openai/gpt-image-2', cost: result.cost_usd }));
  } else {
    console.error('No URL:', JSON.stringify(result));
    process.exit(1);
  }
}
main().catch(err => { console.error('Failed:', err.message); process.exit(1); });
