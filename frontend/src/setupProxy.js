const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy all requests (except static files) to Django backend
  app.use(
    '/',
    createProxyMiddleware({
      target: 'http://localhost:8001',
      changeOrigin: true,
      ws: true,
      // Don't proxy these paths (React static files)
      pathFilter: (path, req) => {
        const excludePaths = [
          '/static/',
          '/sockjs-node',
          '/ws',
          '/__webpack',
          '/hot-update',
          '.js',
          '.css',
          '.map',
          '.json',
          '/manifest.json',
          '/favicon.ico',
          '/logo',
        ];
        return !excludePaths.some(exclude => path.includes(exclude));
      },
    })
  );
};
