/**
 * 美之晨點餐系統 — 後端代理層（Cloudflare Pages Advanced Mode）
 * 目的：前端不再暴露 script.google.com 的真實 /exec 網址，
 *      所有 API 呼叫改走同網域 /api?...，由本 Worker 轉發到 Apps Script。
 * 其餘請求一律交回 Pages 靜態資源（env.ASSETS），_headers 規則照常生效。
 */

// 後端真實網址不寫進版控：本檔位於公開儲存庫，
// 改由 Cloudflare Pages 專案的環境變數 BACKEND_URL 注入（Settings → Environment variables）。
// const BACKEND = env.BACKEND_URL

// 同網域呼叫不需要 CORS；保留只為相容舊 GitHub Pages 前端（遷站驗證期）
const ALLOWED_ORIGINS = [
  "https://tewei02.github.io",
  "https://mzc-breakfast.pages.dev",
  "http://localhost:8000",
  "http://127.0.0.1:8000",
];

function corsHeaders(origin) {
  if (!origin) return {};
  if (!ALLOWED_ORIGINS.includes(origin)) return {};
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
  };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 不是 /api 開頭的請求 → 交給 Pages 靜態資源（含 _headers）
    if (!url.pathname.startsWith("/api")) {
      return env.ASSETS.fetch(request);
    }

    const origin = request.headers.get("Origin") || "";

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    // 後端網址來自環境變數；未設定就明確報錯，不以空字串誤打
    const BACKEND = (env.BACKEND_URL || "").trim();
    if (!BACKEND) {
      return new Response(
        JSON.stringify({ ok: false, msg: "backend_not_configured" }),
        {
          status: 503,
          headers: {
            "Content-Type": "application/json; charset=utf-8",
            "Cache-Control": "no-store",
          },
        }
      );
    }

    // Apps Script 不支援自訂路徑，/api 之後的 query 原樣往後送
    const target = BACKEND + (url.search || "");

    const init = {
      method: request.method,
      headers: { "User-Agent": "mzc-proxy/1.0" },
      redirect: "follow",
    };

    if (request.method === "POST") {
      const ct = request.headers.get("Content-Type") || "";
      init.headers["Content-Type"] = ct || "text/plain;charset=utf-8";
      init.body = await request.text();
    }

    let resp;
    try {
      resp = await fetch(target, init);
    } catch (e) {
      return new Response(JSON.stringify({ ok: false, msg: "proxy_error" }), {
        status: 502,
        headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders(origin) },
      });
    }

    const body = await resp.text();
    return new Response(body, {
      status: resp.status,
      headers: {
        "Content-Type": resp.headers.get("Content-Type") || "application/json; charset=utf-8",
        "Cache-Control": "no-store",
        ...corsHeaders(origin),
      },
    });
  },
};
