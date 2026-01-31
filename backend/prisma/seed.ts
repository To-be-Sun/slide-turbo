import { PrismaClient } from "@prisma/client"

const prisma = new PrismaClient()

async function main() {
  console.log("🌱 Seeding database...")

  // サンプルテンプレートを作成
  const template = await prisma.template.create({
    data: {
      name: "ビジネスプレゼン",
      description: "プロフェッショナルなビジネス向けテンプレート",
      thumbnail: "/business-presentation-template.png",
      slideCount: 5,
      slots: {
        create: [
          {
            slideIndex: 0,
            name: "タイトル",
            type: "title",
            placeholder: "プレゼンのタイトル",
            required: true,
          },
          {
            slideIndex: 0,
            name: "サブタイトル",
            type: "text",
            placeholder: "サブタイトルや日付",
            required: false,
          },
          {
            slideIndex: 1,
            name: "課題",
            type: "title",
            placeholder: "解決したい課題",
            required: true,
          },
          {
            slideIndex: 1,
            name: "課題ポイント",
            type: "list",
            placeholder: "課題を箇条書きで",
            required: true,
          },
        ],
      },
    },
  })

  console.log("✅ Created template:", template.name)

  // テンプレートのスロットを取得
  const templateSlots = await prisma.templateSlot.findMany({
    where: { templateId: template.id },
    orderBy: [{ slideIndex: "asc" }, { createdAt: "asc" }],
  })

  // サンプルプロジェクトを作成
  const project = await prisma.project.create({
    data: {
      name: "Q4事業報告",
      description: "2024年Q4の事業成果報告プレゼン",
      templateId: template.id,
      templateName: template.name,
      status: "IN_PROGRESS",
      slots: {
        create: [
          {
            slotId: templateSlots[0].id,
            slideIndex: 0,
            name: "タイトル",
            type: "title",
            value: "2024年Q4事業報告",
            status: "approved",
          },
          {
            slotId: templateSlots[1].id,
            slideIndex: 0,
            name: "サブタイトル",
            type: "text",
            value: "株式会社サンプル",
            status: "filled",
          },
        ],
      },
      storySections: {
        create: [
          {
            title: "導入",
            content: "2024年Q4の振り返りと成果を共有",
            slideIndices: [0],
            status: "approved",
            order: 0,
          },
        ],
      },
    },
  })

  console.log("✅ Created project:", project.name)
  console.log("🎉 Seeding completed!")
}

main()
  .catch((e) => {
    console.error("❌ Seeding failed:", e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })

