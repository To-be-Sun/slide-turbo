import { GoogleGenerativeAI } from "@google/generative-ai"
import dotenv from "dotenv"

// 環境変数を読み込む（他のモジュールより先に実行される可能性があるため）
dotenv.config()

let genAI: GoogleGenerativeAI | null = null
let defaultModel: ReturnType<GoogleGenerativeAI["getGenerativeModel"]> | null = null

/**
 * Gemini APIクライアントを取得（遅延初期化）
 */
function getGenAI(): GoogleGenerativeAI {
  if (!genAI) {
    const apiKey = process.env.GEMINI_API_KEY
    if (!apiKey) {
      console.error("❌ GEMINI_API_KEY is not set!")
      console.error("📝 Please create a .env file in the backend directory with:")
      console.error("   GEMINI_API_KEY=your_api_key_here")
      console.error("🔗 Get your API key from: https://aistudio.google.com/app/apikey")
      throw new Error(
        "GEMINI_API_KEY environment variable is required. " +
        "Please set it in your .env file. " +
        "Get your API key from: https://aistudio.google.com/app/apikey"
      )
    }
    // APIキーの最初の10文字だけ表示（セキュリティのため）
    const maskedKey = apiKey.substring(0, 10) + "..."
    console.log(`✅ Gemini API key loaded: ${maskedKey}`)
    genAI = new GoogleGenerativeAI(apiKey)
  }
  return genAI
}

/**
 * デフォルトモデルを取得（遅延初期化）
 */
export function getModel() {
  if (!defaultModel) {
    const ai = getGenAI()
    // Gemini 3 Pro (Nanobanana Pro) モデルを使用
    defaultModel = ai.getGenerativeModel({ 
      model: "gemini-3.0-pro" // または "gemini-3.0-pro-image" など、利用可能なモデル名
    })
  }
  return defaultModel
}

/**
 * フォールバック: 利用可能なモデルを試す
 */
export async function getAvailableModel() {
  const ai = getGenAI()
  
  try {
    // まず gemini-3.0-pro を試す
    const testModel = ai.getGenerativeModel({ model: "gemini-3.0-pro" })
    await testModel.generateContent("test")
    return testModel
  } catch (error) {
    console.warn("gemini-3.0-pro not available, trying gemini-pro")
    // フォールバック
    return ai.getGenerativeModel({ model: "gemini-pro" })
  }
}

// 後方互換性のため（getter関数としてエクスポート）
export function getGenAIClient() {
  return getGenAI()
}

