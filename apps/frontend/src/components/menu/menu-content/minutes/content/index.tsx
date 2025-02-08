import { useRef, useState, useEffect } from "react"
import { db } from "@/firebase"
import { doc, onSnapshot } from "firebase/firestore"
import { useSelector } from "react-redux"
import { RootState } from "@/store"
import styles from "./index.module.scss"

interface AgendaItem {
  id: string
  topic: string
  duration: number
  completed: boolean
}

interface DecisionItem {
  id: string
  text: string
}

interface ActionPlanItem {
  id: string
  task: string
  assigned_to: string
  due_date: string
}

let lastScrollTop = 0

const Content = () => {
  const contentRef = useRef<HTMLElement>(null)
  const [humanScroll, setHumanScroll] = useState(false)
  const [agenda, setAgenda] = useState<AgendaItem[]>([])
  const [decisions, setDecisions] = useState<DecisionItem[]>([])
  const [actionPlan, setActionPlan] = useState<ActionPlanItem[]>([])
  const meetingId = useSelector((state: RootState) => state.global.meetingId)

  useEffect(() => {
    if (!meetingId) {
      alert("エラー: meetingId が指定されていません")
      return
    }
    const minutesDocRef = doc(db, "meetings", meetingId, "minutes", "all_minutes")

    const unsubscribe = onSnapshot(minutesDocRef, (docSnapshot) => {
      if (docSnapshot.exists()) {
        const data = docSnapshot.data()
        setAgenda(data.agenda || [])
        setDecisions(data.decisions || [])
        setActionPlan(data.action_plan || [])
      }
    })

    return () => unsubscribe()
  }, [meetingId])

  const onScroll = (e: any) => {
    const scrollTop = contentRef.current?.scrollTop ?? 0
    if (scrollTop < lastScrollTop) {
      setHumanScroll(true)
    }
    lastScrollTop = scrollTop
  }

  useEffect(() => {
    contentRef.current?.addEventListener("scroll", onScroll)
    return () => {
      contentRef.current?.removeEventListener("scroll", onScroll)
      lastScrollTop = 0
    }
  }, [contentRef])

  useEffect(() => {
    if (humanScroll) {
      return
    }
    if (contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight
    }
  }, [agenda, decisions, actionPlan, humanScroll])

  return (
    <section className={styles.record} ref={contentRef}>
      <div className={styles.section}>
        <h3>Agenda</h3>
        <ul>
          {agenda.map((item, index) => (
            <li key={item.id} className={item.completed ? styles.completed : ""}>
              {item.completed ? "✅ " : "🔲 "} {`${item.topic}`}
            </li>
          ))}
        </ul>
      </div>

      <div className={styles.section}>
        <h3>Decisions</h3>
        <ul>
          {decisions.map((decision) => (
            <li key={decision.id}>{decision.text}</li>
          ))}
        </ul>
      </div>

      <div className={styles.section}>
        <h3>Action Plan</h3>
        <ul>
          {actionPlan.map((item) => (
            <li key={item.id}>
              {item.task} - 担当: {item.assigned_to} - 期限: {item.due_date}
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}

export default Content
