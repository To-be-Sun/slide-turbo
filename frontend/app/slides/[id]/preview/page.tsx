"use client";

import { useParams, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, FileText, Check, AlertCircle, ExternalLink } from "lucide-react";

/**
 * スライドプレビュー＆エクスポート実験ページ
 * 
 * 機能:
 * 1. スライドのHTMLプレビュー表示
 * 2. バージョン選択
 * 3. Google Slidesエクスポート
 */

interface ExportResponse {
  presentation_id: string;
  presentation_url: string;
  edit_url: string;
}

interface SlideData {
  id: string;
  title: string;
  versions: number[];
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function SlidePreviewPage() {
  const params = useParams();
  const router = useRouter();
  const slideId = params.id as string;

  // State
  const [slideData, setSlideData] = useState<SlideData | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<number>(1);
  const [htmlContent, setHtmlContent] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exportResult, setExportResult] = useState<ExportResponse | null>(null);
  
  // Export dialog state
  const [dialogOpen, setDialogOpen] = useState(false);
  const [presentationTitle, setPresentationTitle] = useState("");
  const [accessToken, setAccessToken] = useState("");

  // スライドデータとHTMLプレビューの取得
  useEffect(() => {
    fetchSlidePreview();
  }, [slideId, selectedVersion]);

  const fetchSlidePreview = async () => {
    setLoading(true);
    setError(null);

    try {
      // HTMLプレビューを取得
      const response = await fetch(
        `${BACKEND_URL}/api/slides/${slideId}/preview?version_num=${selectedVersion}`,
        {
          headers: {
            "Accept": "text/html",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`プレビュー取得失敗: ${response.status}`);
      }

      const html = await response.text();
      setHtmlContent(html);

      // スライド情報を取得（仮実装 - 実際はAPIから取得）
      if (!slideData) {
        setSlideData({
          id: slideId,
          title: "スライドタイトル",
          versions: [1, 2, 3], // 実際はAPIから取得
        });
        setPresentationTitle(`スライド ${slideId} (v${selectedVersion})`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "エラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    if (!accessToken.trim()) {
      setError("Google OAuth2 アクセストークンを入力してください");
      return;
    }

    setExporting(true);
    setError(null);
    setExportResult(null);

    try {
      const response = await fetch(
        `${BACKEND_URL}/api/slides/${slideId}/export/google-slides`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Google-Access-Token": accessToken,
          },
          body: JSON.stringify({
            version_num: selectedVersion,
            presentation_title: presentationTitle || `Slide ${slideId} v${selectedVersion}`,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `エクスポート失敗: ${response.status}`
        );
      }

      const result: ExportResponse = await response.json();
      setExportResult(result);
      
      // 3秒後にダイアログを閉じる
      setTimeout(() => {
        setDialogOpen(false);
      }, 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "エクスポートエラー");
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                onClick={() => router.push("/slides")}
              >
                ← 戻る
              </Button>
              <div>
                <h1 className="text-2xl font-bold">スライドプレビュー</h1>
                <p className="text-sm text-gray-500">ID: {slideId}</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {/* バージョン選択 */}
              <div className="flex items-center gap-2">
                <Label>バージョン:</Label>
                <Select
                  value={selectedVersion.toString()}
                  onValueChange={(value) => setSelectedVersion(parseInt(value))}
                >
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {slideData?.versions.map((v) => (
                      <SelectItem key={v} value={v.toString()}>
                        v{v}
                      </SelectItem>
                    )) || (
                      <>
                        <SelectItem value="1">v1</SelectItem>
                        <SelectItem value="2">v2</SelectItem>
                        <SelectItem value="3">v3</SelectItem>
                      </>
                    )}
                  </SelectContent>
                </Select>
              </div>

              {/* エクスポートダイアログ */}
              <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="gap-2">
                    <FileText className="w-4 h-4" />
                    Google Slidesへエクスポート
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[500px]">
                  <DialogHeader>
                    <DialogTitle>Google Slidesへエクスポート</DialogTitle>
                    <DialogDescription>
                      スライドをGoogle Slidesにエクスポートします
                    </DialogDescription>
                  </DialogHeader>

                  {exportResult ? (
                    <div className="space-y-4">
                      <Alert className="bg-green-50 border-green-200">
                        <Check className="h-4 w-4 text-green-600" />
                        <AlertDescription className="text-green-800">
                          エクスポート成功！
                        </AlertDescription>
                      </Alert>

                      <div className="space-y-2">
                        <div className="p-3 bg-gray-50 rounded-md">
                          <p className="text-sm font-medium mb-1">
                            プレゼンテーションID:
                          </p>
                          <p className="text-xs text-gray-600 font-mono break-all">
                            {exportResult.presentation_id}
                          </p>
                        </div>

                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            className="flex-1 gap-2"
                            onClick={() =>
                              window.open(exportResult.presentation_url, "_blank")
                            }
                          >
                            <ExternalLink className="w-4 h-4" />
                            表示用URL
                          </Button>
                          <Button
                            className="flex-1 gap-2"
                            onClick={() =>
                              window.open(exportResult.edit_url, "_blank")
                            }
                          >
                            <ExternalLink className="w-4 h-4" />
                            編集用URL
                          </Button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="title">プレゼンテーションタイトル</Label>
                        <Input
                          id="title"
                          placeholder="例: 営業資料 2026 Q1"
                          value={presentationTitle}
                          onChange={(e) => setPresentationTitle(e.target.value)}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="token">
                          Google OAuth2 アクセストークン *
                        </Label>
                        <Input
                          id="token"
                          type="password"
                          placeholder="ya29...."
                          value={accessToken}
                          onChange={(e) => setAccessToken(e.target.value)}
                        />
                        <p className="text-xs text-gray-500">
                          ※ OAuth2 Playground等で取得したアクセストークン
                        </p>
                      </div>

                      {error && (
                        <Alert variant="destructive">
                          <AlertCircle className="h-4 w-4" />
                          <AlertDescription>{error}</AlertDescription>
                        </Alert>
                      )}
                    </div>
                  )}

                  {!exportResult && (
                    <DialogFooter>
                      <Button
                        variant="outline"
                        onClick={() => setDialogOpen(false)}
                        disabled={exporting}
                      >
                        キャンセル
                      </Button>
                      <Button
                        onClick={handleExport}
                        disabled={exporting || !accessToken.trim()}
                      >
                        {exporting ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            エクスポート中...
                          </>
                        ) : (
                          "エクスポート"
                        )}
                      </Button>
                    </DialogFooter>
                  )}
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="container mx-auto px-4 py-8">
        {loading ? (
          <Card>
            <CardContent className="flex items-center justify-center py-20">
              <div className="text-center space-y-4">
                <Loader2 className="w-12 h-12 animate-spin mx-auto text-gray-400" />
                <p className="text-gray-500">プレビューを読み込み中...</p>
              </div>
            </CardContent>
          </Card>
        ) : error ? (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>プレビュー (バージョン {selectedVersion})</CardTitle>
            </CardHeader>
            <CardContent>
              {/* HTMLプレビュー */}
              <div className="border rounded-lg overflow-hidden bg-white">
                <iframe
                  srcDoc={htmlContent}
                  className="w-full h-[600px]"
                  title="スライドプレビュー"
                  sandbox="allow-scripts"
                />
              </div>

              {/* デバッグ情報 */}
              <details className="mt-4">
                <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700 font-medium">
                  📄 HTMLソースを表示 ({htmlContent.length.toLocaleString()} 文字)
                </summary>
                <div className="mt-3 border rounded-md bg-gray-900 p-4 max-h-96 overflow-auto">
                  <pre className="text-xs text-gray-100 font-mono whitespace-pre-wrap break-words">
                    <code>{htmlContent}</code>
                  </pre>
                </div>
              </details>
            </CardContent>
          </Card>
        )}

        {/* 使い方ガイド */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg">使い方</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex items-start gap-2">
              <span className="font-bold">1.</span>
              <p>上部のバージョン選択でプレビューするバージョンを選択</p>
            </div>
            <div className="flex items-start gap-2">
              <span className="font-bold">2.</span>
              <p>プレビューで内容を確認</p>
            </div>
            <div className="flex items-start gap-2">
              <span className="font-bold">3.</span>
              <p>
                「Google Slidesへエクスポート」ボタンをクリック
              </p>
            </div>
            <div className="flex items-start gap-2">
              <span className="font-bold">4.</span>
              <p>
                Google OAuth2アクセストークンを入力
                <br />
                <a
                  href="https://developers.google.com/oauthplayground/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline ml-2"
                >
                  → OAuth2 Playground
                </a>
              </p>
            </div>
            <div className="flex items-start gap-2">
              <span className="font-bold">5.</span>
              <p>エクスポート完了後、Google Slidesで開く</p>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
