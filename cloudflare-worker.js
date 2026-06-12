/**
 * cloudflare-worker.js
 * ────────────────────
 * texlive.net 의 CORS 프록시 — Cloudflare Workers (무료 플랜, 100k req/day)
 *
 * 【배포 방법 — 5분】
 *  1. https://workers.cloudflare.com 에서 무료 계정 생성
 *  2. "Create a Worker" 클릭
 *  3. 이 파일 전체를 에디터에 붙여넣기
 *  4. 배포(Save and Deploy) → 워커 URL 확인
 *     예: https://latex-proxy.yourname.workers.dev
 *  5. index.html 상단의 COMPILE_PROXY 값을 해당 URL로 변경:
 *     const COMPILE_PROXY = 'https://latex-proxy.yourname.workers.dev';
 *  6. git commit & push
 */

const UPSTREAM = 'https://texlive.net/cgi-bin/latexcgi';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Max-Age':       '86400',
};

export default {
  async fetch(request) {
    /* preflight */
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    /* texlive.net 으로 그대로 전달 */
    let upstream;
    try {
      upstream = await fetch(UPSTREAM, {
        method: 'POST',
        headers: request.headers,
        body:    request.body,
      });
    } catch (e) {
      return new Response('upstream error: ' + e.message, { status: 502 });
    }

    /* 응답에 CORS 헤더 추가 */
    const headers = new Headers(upstream.headers);
    for (const [k, v] of Object.entries(CORS_HEADERS)) headers.set(k, v);

    return new Response(upstream.body, {
      status:  upstream.status,
      headers,
    });
  },
};
