import { NextRequest, NextResponse } from "next/server"

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:3001"

export async function GET(
  request: NextRequest,
  { params }: { params: { slideIndex: string } }
) {
  try {
    const { searchParams } = new URL(request.url)
    const html = searchParams.get("html")

    if (!html) {
      return NextResponse.json(
        { success: false, error: "html query parameter is required" },
        { status: 400 }
      )
    }

    const slideIndex = parseInt(params.slideIndex)
    if (isNaN(slideIndex)) {
      return NextResponse.json(
        { success: false, error: "Invalid slide index" },
        { status: 400 }
      )
    }

    const response = await fetch(
      `${BACKEND_URL}/api/slides/render/${slideIndex}?html=${encodeURIComponent(html)}`,
      {
        method: "GET",
      }
    )

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(
        { success: false, error: error.message || "Failed to render slide" },
        { status: response.status }
      )
    }

    // 画像データをそのまま返す
    const imageBuffer = await response.arrayBuffer()
    return new NextResponse(imageBuffer, {
      headers: {
        "Content-Type": "image/png",
      },
    })
  } catch (error) {
    console.error("Error in render API route:", error)
    return NextResponse.json(
      { success: false, error: "Internal server error" },
      { status: 500 }
    )
  }
}

