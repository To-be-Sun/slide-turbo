// 環境変数を最初に読み込む（他のモジュールより先に）
import dotenv from "dotenv"
dotenv.config()

import express from "express"
import cors from "cors"
import slidesRouter from "./routes/slides.js"
import googleSlidesRouter from "./routes/google-slides.js"
import projectsRouter from "./routes/projects.js"
import templatesRouter from "./routes/templates.js"

const app = express()
const PORT = process.env.PORT || 3001

// ミドルウェア
app.use(cors({
  origin: process.env.FRONTEND_URL || "http://localhost:3000",
  credentials: true,
}))
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

// ヘルスチェック
app.get("/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() })
})

// API ルート
app.use("/api/slides", slidesRouter)
app.use("/api/google-slides", googleSlidesRouter)
app.use("/api/projects", projectsRouter)
app.use("/api/templates", templatesRouter)

// エラーハンドリング
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error("Error:", err)
  res.status(500).json({
    success: false,
    error: "Internal server error",
    message: err.message,
  })
})

// サーバー起動
app.listen(PORT, () => {
  console.log(`🚀 Backend server running on http://localhost:${PORT}`)
  console.log(`📝 Health check: http://localhost:${PORT}/health`)
})

