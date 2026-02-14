"use client";

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Code, Presentation } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuth } from "@/lib/auth";
import { getGoogleAuthUrl, googleCallback } from "@/lib/api";

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center">
          <div className="animate-pulse text-muted-foreground">Loading...</div>
        </div>
      }
    >
      <LoginContent />
    </Suspense>
  );
}

function LoginContent() {
  const { user, loading, login, devLogin, isDevMode } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  // 既にログイン済みならダッシュボードへ
  useEffect(() => {
    if (!loading && user) {
      router.replace("/");
    }
  }, [user, loading, router]);

  // 開発モード: 自動ログイン（コールバックでない場合）
  //useEffect(() => {
  //  if (!loading && !user && isDevMode && !searchParams.get("code")) {
  //    devLogin();
  //  }
  //}, [loading, user, isDevMode, searchParams, devLogin]);

  // Google OAuth コールバック処理
  useEffect(() => {
    const code = searchParams.get("code");
    if (!code) return;

    googleCallback(code)
      .then((res) => {
        login(res.access_token, res.user, res.google_access_token ?? null);
        router.replace("/");
      })
      .catch((err) => {
        console.error("Login failed:", err);
      });
  }, [searchParams, login, router]);

  const handleGoogleLogin = () => {
    window.location.href = getGoogleAuthUrl();
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10">
            <Presentation className="h-7 w-7 text-primary" />
          </div>
          <CardTitle className="text-2xl">Slide Turbo</CardTitle>
          <CardDescription>
            AI でプレゼンテーションを高速作成
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {/* Google OAuth */}
          <Button
            onClick={handleGoogleLogin}
            variant="outline"
            size="lg"
            className="w-full gap-3"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5">
              <path
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
                fill="#4285F4"
              />
              <path
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                fill="#34A853"
              />
              <path
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                fill="#FBBC05"
              />
              <path
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                fill="#EA4335"
              />
            </svg>
            Google でログイン
          </Button>

          {/* Dev Mode Login */}
          {isDevMode && (
            <>
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-card px-2 text-muted-foreground">
                    開発モード
                  </span>
                </div>
              </div>
              <Button
                onClick={devLogin}
                variant="secondary"
                size="lg"
                className="w-full gap-3"
              >
                <Code className="h-5 w-5" />
                Dev ユーザーでログイン
              </Button>
              <p className="text-center text-xs text-muted-foreground">
                バックエンド不要でUIを確認できます
              </p>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
