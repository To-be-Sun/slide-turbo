import { google } from "googleapis"
import type { OAuth2Client } from "google-auth-library"
import { readFileSync, readdirSync } from "fs"
import { join } from "path"
import { fileURLToPath } from "url"
import { dirname } from "path"

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

let authClient: OAuth2Client | null = null

interface GoogleCredentials {
  web?: {
    client_id: string
    client_secret: string
    redirect_uris?: string[]
  }
  installed?: {
    client_id: string
    client_secret: string
    redirect_uris?: string[]
  }
}

/**
 * JSONファイルから認証情報を読み込む
 */
function loadCredentialsFromFile(): { clientId: string; clientSecret: string } | null {
  // 環境変数でJSONファイルのパスが指定されている場合
  const credentialsPath = process.env.GOOGLE_CREDENTIALS_PATH
  
  // デフォルトのパスを試す（プロジェクトルートのclient_secret_*.json）
  const possiblePaths = [
    credentialsPath,
    join(__dirname, "../../client_secret.json"),
    join(__dirname, "../../client_secret_*.json"), // ワイルドカードは後で処理
  ].filter((p): p is string => p !== undefined)

  // ワイルドカードパターンでファイルを検索
  if (!credentialsPath) {
    try {
      const files = readdirSync(join(__dirname, "../../"))
      const clientSecretFile = files.find((f: string) => f.startsWith("client_secret_") && f.endsWith(".json"))
      if (clientSecretFile) {
        possiblePaths.push(join(__dirname, "../../", clientSecretFile))
      }
    } catch (error) {
      // ファイルが見つからない場合は無視
    }
  }

  for (const path of possiblePaths) {
    try {
      if (path.includes("*")) continue // ワイルドカードはスキップ
      
      const fileContent = readFileSync(path, "utf-8")
      const credentials: GoogleCredentials = JSON.parse(fileContent)
      
      // web または installed のいずれかから取得
      const creds = credentials.web || credentials.installed
      if (creds?.client_id && creds?.client_secret) {
        return {
          clientId: creds.client_id,
          clientSecret: creds.client_secret,
        }
      }
    } catch (error) {
      // ファイルが見つからない、または読み込めない場合は次を試す
      continue
    }
  }

  return null
}

/**
 * Google Slides API認証クライアントを取得
 */
export function getGoogleSlidesAuth(): OAuth2Client {
  if (authClient) {
    return authClient
  }

  let clientId: string | undefined
  let clientSecret: string | undefined

  // まずJSONファイルから読み込む
  const fileCredentials = loadCredentialsFromFile()
  if (fileCredentials) {
    clientId = fileCredentials.clientId
    clientSecret = fileCredentials.clientSecret
    console.log("✅ Google認証情報をJSONファイルから読み込みました")
  } else {
    // JSONファイルがない場合は環境変数から取得
    clientId = process.env.GOOGLE_CLIENT_ID
    clientSecret = process.env.GOOGLE_CLIENT_SECRET
    console.log("✅ Google認証情報を環境変数から読み込みました")
  }

  const redirectUri = process.env.GOOGLE_REDIRECT_URI || "http://localhost:3001/auth/callback"

  if (!clientId || !clientSecret) {
    throw new Error(
      "Google認証情報が見つかりません。\n" +
      "以下のいずれかの方法で設定してください：\n" +
      "1. JSONファイル: backend/client_secret_*.json を配置\n" +
      "2. 環境変数: GOOGLE_CLIENT_ID と GOOGLE_CLIENT_SECRET を設定\n" +
      "詳細は docs/GOOGLE_API_SETUP.md を参照してください"
    )
  }

  authClient = new google.auth.OAuth2(clientId, clientSecret, redirectUri)

  // リフレッシュトークンがある場合は設定
  if (process.env.GOOGLE_REFRESH_TOKEN) {
    authClient.setCredentials({
      refresh_token: process.env.GOOGLE_REFRESH_TOKEN,
    })
  }

  return authClient
}

/**
 * Google Slides APIクライアントを取得
 */
export function getGoogleSlidesClient() {
  const auth = getGoogleSlidesAuth()
  return google.slides({ version: "v1", auth })
}

/**
 * 認証URLを生成
 */
export function getAuthUrl(): string {
  const auth = getGoogleSlidesAuth()
  return auth.generateAuthUrl({
    access_type: "offline",
    scope: [
      "https://www.googleapis.com/auth/presentations.readonly",
      "https://www.googleapis.com/auth/drive.readonly",
    ],
  })
}

/**
 * 認証トークンを設定
 */
export async function setAuthToken(code: string): Promise<void> {
  const auth = getGoogleSlidesAuth()
  const { tokens } = await auth.getToken(code)
  auth.setCredentials(tokens)
  
  if (tokens.refresh_token) {
    console.log("Refresh token:", tokens.refresh_token)
    console.log("Set this as GOOGLE_REFRESH_TOKEN in your .env file")
  }
}

