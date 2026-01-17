import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Repo root is two levels up from frontend/scripts
const REPO_ROOT = path.resolve(__dirname, '../../');

const SOURCE_PATH = path.join(REPO_ROOT, 'backend/models/recommend_model/recommend_output.csv');
const DEST_DIR = path.join(REPO_ROOT, 'frontend/public');
const DEST_PATH = path.join(DEST_DIR, 'reco.csv');

console.log('Syncing Recommendation CSV...');
console.log(`Source: ${SOURCE_PATH}`);
console.log(`Dest:   ${DEST_PATH}`);

if (!fs.existsSync(SOURCE_PATH)) {
    console.error(`❌ Source file not found: ${SOURCE_PATH}`);
    process.exit(1);
}

if (!fs.existsSync(DEST_DIR)) {
    fs.mkdirSync(DEST_DIR, { recursive: true });
}

try {
    fs.copyFileSync(SOURCE_PATH, DEST_PATH);
    console.log('✅ CSV copied successfully!');
} catch (error) {
    console.error('❌ Error copying CSV:', error);
    process.exit(1);
}
