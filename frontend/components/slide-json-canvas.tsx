"use client";

import { z } from "zod";

const SLIDE_WIDTH_PT = 960;
const SLIDE_HEIGHT_PT = 540;
const toPctX = (pt: number) => (pt / SLIDE_WIDTH_PT) * 100;
const toPctY = (pt: number) => (pt / SLIDE_HEIGHT_PT) * 100;
const ptToPx = (pt: number) => pt * (96 / 72);

const transformSchema = z.object({
  scaleX: z.number().optional().default(1),
  scaleY: z.number().optional().default(1),
  translateX: z.number().optional().default(0),
  translateY: z.number().optional().default(0),
});

const dimensionSchema = z.object({
  magnitude: z.number(),
  unit: z.string().optional(),
});

const sizeSchema = z.object({
  width: dimensionSchema,
  height: dimensionSchema,
});

const textStyleSchema = z.object({
  fontSize: z
    .object({
      magnitude: z.number(),
      unit: z.string().optional(),
    })
    .optional(),
  bold: z.boolean().optional(),
  fontFamily: z.string().optional(),
  foregroundColor: z
    .object({
      opaqueColor: z
        .object({
          themeColor: z.string().optional(),
        })
        .optional(),
    })
    .optional(),
});

const textElementSchema = z.object({
  startIndex: z.number().optional(),
  endIndex: z.number().optional(),
  textRun: z
    .object({
      content: z.string().optional(),
      style: textStyleSchema.optional(),
    })
    .optional(),
  paragraphMarker: z
    .object({
      style: z
        .object({
          bullet: z
            .object({
              listId: z.string().optional(),
              nestingLevel: z.number().optional(),
            })
            .optional(),
        })
        .optional(),
    })
    .optional(),
});

const pageElementSchema = z.object({
  objectId: z.string().optional(),
  transform: transformSchema.optional(),
  size: sizeSchema.optional(),
  shape: z
    .object({
      shapeType: z.string().optional(),
      text: z
        .object({
          textElements: z.array(textElementSchema).optional(),
        })
        .optional(),
    })
    .optional(),
  image: z
    .object({
      contentUrl: z.string().optional(),
    })
    .optional(),
});

const slideSchema = z.object({
  objectId: z.string().optional(),
  pageType: z.string().optional(),
  pageElements: z.array(pageElementSchema).optional(),
});

type NormalizedElement =
      | {
      id: string;
      type: "text";
      leftPct: number;
      topPct: number;
      widthPct: number;
      heightPct: number;
      lines: string[];
      bulleted: boolean;
      fontSizePt: number;
      bold: boolean;
      color: string;
      fontFamily: string;
    }
  | {
      id: string;
      type: "image";
      leftPct: number;
      topPct: number;
      widthPct: number;
      heightPct: number;
      contentUrl: string;
    }
  | {
      id: string;
      type: "unknown";
      leftPct: number;
      topPct: number;
      widthPct: number;
      heightPct: number;
    };

type NormalizedSlide = {
  objectId: string;
  elements: NormalizedElement[];
  error?: string;
};

function themeColorToCss(themeColor?: string): string {
  if (themeColor === "DARK1") return "#111827";
  if (themeColor === "LIGHT1") return "#ffffff";
  return "#111827";
}

function resolveFontFamily(fontFamily?: string): string {
  const raw = (fontFamily ?? "").trim();
  const normalized = raw.toLowerCase();

  if (!normalized) {
    return 'var(--font-slide-sans), "Noto Sans JP", sans-serif';
  }

  if (
    normalized.includes("serif") ||
    normalized.includes("times") ||
    normalized.includes("mincho")
  ) {
    return `var(--font-slide-serif), "${raw}", serif`;
  }

  if (
    normalized.includes("poppins") ||
    normalized.includes("poppin")
  ) {
    return `var(--font-slide-poppins), "Poppins", var(--font-slide-sans), "Noto Sans JP", sans-serif`;
  }

  if (
    normalized.includes("sans") ||
    normalized.includes("arial") ||
    normalized.includes("gothic") ||
    normalized.includes("helvetica")
  ) {
    return `var(--font-slide-sans), "${raw}", sans-serif`;
  }

  return `"${raw}", var(--font-slide-sans), "Noto Sans JP", sans-serif`;
}

function normalizeSlide(input: unknown): NormalizedSlide {
  const parsed = slideSchema.safeParse(input);
  if (!parsed.success) {
    return {
      objectId: "invalid-slide",
      elements: [],
      error: "Invalid slide JSON structure",
    };
  }

  const slide = parsed.data;
  const elements: NormalizedElement[] = (slide.pageElements ?? []).map((el, i) => {
    const id = el.objectId ?? `elem-${i + 1}`;
    const transform = el.transform ?? {
      scaleX: 1,
      scaleY: 1,
      translateX: 0,
      translateY: 0,
    };
    const widthPt = (el.size?.width.magnitude ?? 300) * transform.scaleX;
    const heightPt = (el.size?.height.magnitude ?? 120) * transform.scaleY;
    const leftPct = toPctX(transform.translateX);
    const topPct = toPctY(transform.translateY);
    const widthPct = toPctX(widthPt);
    const heightPct = toPctY(heightPt);

    if (el.shape?.text?.textElements) {
      const textElements = el.shape.text.textElements;
      const fullText = textElements
        .map((x) => x.textRun?.content ?? "")
        .join("");
      const lines = fullText
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean);
      const firstStyledRun = textElements.find((x) => x.textRun?.style)?.textRun;
      const style = firstStyledRun?.style;
      const bulleted = textElements.some((x) => Boolean(x.paragraphMarker?.style?.bullet));
      return {
        id,
        type: "text",
        leftPct,
        topPct,
        widthPct,
        heightPct,
        lines: lines.length > 0 ? lines : [""],
        bulleted,
        fontSizePt: style?.fontSize?.magnitude ?? 18,
        bold: Boolean(style?.bold),
        color: themeColorToCss(style?.foregroundColor?.opaqueColor?.themeColor),
        fontFamily: resolveFontFamily(style?.fontFamily),
      };
    }

    if (el.image?.contentUrl) {
      return {
        id,
        type: "image",
        leftPct,
        topPct,
        widthPct,
        heightPct,
        contentUrl: el.image.contentUrl,
      };
    }

    return {
      id,
      type: "unknown",
      leftPct,
      topPct,
      widthPct,
      heightPct,
    };
  });

  return {
    objectId: slide.objectId ?? "slide",
    elements,
  };
}

export function SlideJsonCanvas({
  slide,
  debug = false,
}: {
  slide: unknown;
  debug?: boolean;
}) {
  const normalized = normalizeSlide(slide);
  if (normalized.error) {
    return (
      <pre className="h-full overflow-auto p-4 text-xs text-black">
        {JSON.stringify(slide, null, 2)}
      </pre>
    );
  }

  return (
    <div className="relative h-full w-full overflow-hidden rounded-lg bg-white">
      {normalized.elements.map((el) => {
        if (el.type === "text") {
          return (
            <div
              key={el.id}
              className="absolute overflow-hidden"
              style={{
                left: `${el.leftPct}%`,
                top: `${el.topPct}%`,
                width: `${el.widthPct}%`,
                height: `${el.heightPct}%`,
                color: el.color,
                fontFamily: el.fontFamily,
                fontSize: ptToPx(el.fontSizePt),
                fontWeight: el.bold ? 700 : 400,
                lineHeight: 1.35,
              }}
            >
              {el.bulleted ? (
                <ul className="list-disc pl-6">
                  {el.lines.map((line, i) => (
                    <li key={`${el.id}-line-${i}`}>{line}</li>
                  ))}
                </ul>
              ) : (
                <div className="whitespace-pre-wrap">{el.lines.join("\n")}</div>
              )}
            </div>
          );
        }

        if (el.type === "image") {
          return (
            <img
              key={el.id}
              src={el.contentUrl}
              alt=""
              className="absolute object-cover"
              style={{
                left: `${el.leftPct}%`,
                top: `${el.topPct}%`,
                width: `${el.widthPct}%`,
                height: `${el.heightPct}%`,
              }}
            />
          );
        }

        return (
          <div
            key={el.id}
            className="absolute rounded border border-dashed border-gray-300 bg-gray-100/60"
            style={{
              left: `${el.leftPct}%`,
              top: `${el.topPct}%`,
              width: `${el.widthPct}%`,
              height: `${el.heightPct}%`,
            }}
          />
        );
      })}

      {debug ? (
        <pre className="pointer-events-none absolute bottom-2 right-2 max-h-40 max-w-[40%] overflow-auto rounded border bg-white/95 p-2 text-[10px] text-gray-700">
          {JSON.stringify(slide, null, 2)}
        </pre>
      ) : null}
    </div>
  );
}
