const express = require("express");
const { Pool } = require("pg");
const { nanoid } = require("nanoid");
const cors = require("cors");

const app = express();
app.use(express.json());
app.use(cors());

// ---------------------------
// DATABASE CONNECTION
// ---------------------------
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false }
});

// ---------------------------
// INIT DATABASE
// ---------------------------
async function initDB() {
    await pool.query(`
        CREATE TABLE IF NOT EXISTS links (
            code TEXT PRIMARY KEY,
            long_url TEXT NOT NULL,
            click_count INTEGER DEFAULT 0,
            last_clicked TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        );
    `);
}
initDB();

// ---------------------------
// URL VALIDATION
// ---------------------------
function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

// ---------------------------
// 1. HEALTHCHECK
// ---------------------------
app.get("/healthz", (req, res) => {
    res.status(200).send("ok");
});

// ---------------------------
// 2. CREATE SHORT LINK
// ---------------------------
app.post("/links", async (req, res) => {
    let { longUrl, code } = req.body;

    if (!isValidUrl(longUrl)) {
        return res.status(400).json({ error: "Invalid URL format" });
    }

    if (!code) {
        code = nanoid(6);
    }

    // Check duplicate
    const dup = await pool.query("SELECT code FROM links WHERE code=$1", [code]);
    if (dup.rows.length > 0) {
        return res.status(409).json({ error: "Code already exists" });
    }

    await pool.query(
        "INSERT INTO links (code, long_url) VALUES ($1, $2)",
        [code, longUrl]
    );

    res.json({
        code,
        longUrl,
        shortUrl: `${req.protocol}://${req.get("host")}/${code}`
    });
});

// ---------------------------
// 3. LIST ALL LINKS
// ---------------------------
app.get("/links", async (req, res) => {
    const data = await pool.query("SELECT * FROM links ORDER BY created_at DESC");
    res.json(data.rows);
});

// ---------------------------
// 4. DELETE A LINK
// ---------------------------
app.delete("/links/:code", async (req, res) => {
    const { code } = req.params;

    const result = await pool.query("DELETE FROM links WHERE code=$1", [code]);

    if (result.rowCount === 0) {
        return res.status(404).json({ error: "Not found" });
    }

    res.json({ status: "deleted" });
});

// ---------------------------
// 5. REDIRECT LOGIC
// ---------------------------
app.get("/:code", async (req, res, next) => {
    const { code } = req.params;

    // Skip reserved routes
    if (["dashboard", "code", "healthz"].includes(code)) {
        return next();
    }

    const found = await pool.query("SELECT * FROM links WHERE code=$1", [code]);

    if (found.rows.length === 0) {
        return res.status(404).send("Link not found");
    }

    const url = found.rows[0].long_url;

    await pool.query(
        "UPDATE links SET click_count = click_count + 1, last_clicked = NOW() WHERE code=$1",
        [code]
    );

    return res.redirect(302, url);
});

// ---------------------------
// 6. DASHBOARD UI
// ---------------------------
app.get("/dashboard", async (req, res) => {
    const data = await pool.query("SELECT * FROM links ORDER BY created_at DESC");

    const rows = data.rows.map(l => `
        <tr>
            <td>${l.code}</td>
            <td>${l.long_url}</td>
            <td>${l.click_count}</td>
            <td>${l.last_clicked || "Never"}</td>
            <td><button onclick="deleteLink('${l.code}')">Delete</button></td>
        </tr>
    `).join("");

    res.send(`
        <html>
        <body>
            <h1>Dashboard</h1>

            <h3>Add new link</h3>
            <input id="url" placeholder="Long URL" />
            <input id="code" placeholder="Custom code (optional)" />
            <button onclick="addLink()">Add</button>

            <h3>All Links</h3>
            <table border="1">
                <tr><th>Code</th><th>URL</th><th>Clicks</th><th>Last Click</th><th>Actions</th></tr>
                ${rows}
            </table>

<script>
async function addLink() {
    const longUrl = document.getElementById("url").value;
    const code = document.getElementById("code").value;

    let res = await fetch("/links", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ longUrl, code })
    });

    if (res.status == 409) alert("Code already exists!");
    location.reload();
}

async function deleteLink(code) {
    await fetch("/links/" + code, { method: "DELETE" });
    location.reload();
}
</script>

        </body>
        </html>
    `);
});

// ---------------------------
// 7. STATS PAGE
// ---------------------------
app.get("/code/:code", async (req, res) => {
    const { code } = req.params;

    const data = await pool.query("SELECT * FROM links WHERE code=$1", [code]);

    if (data.rows.length === 0) {
        return res.status(404).send("Not found");
    }

    const link = data.rows[0];

    res.send(`
        <html>
        <body>
            <h1>Stats for /${code}</h1>
            <p><b>Original URL:</b> ${link.long_url}</p>
            <p><b>Total Clicks:</b> ${link.click_count}</p>
            <p><b>Last Clicked:</b> ${link.last_clicked || "Never"}</p>
            <p><b>Created:</b> ${link.created_at}</p>
        </body>
        </html>
    `);
});

// ---------------------------
// START SERVER
// ---------------------------
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log("Server running on port " + PORT));
