import Avatar from "@/components/avatar"
import { ICommentItem } from "@/types"
import { useMemo, useRef, useState, useEffect } from "react"
import { db } from "@/firebase"
import { collection, onSnapshot, orderBy, query } from "firebase/firestore"
import { useSelector } from "react-redux"
import { RootState } from "@/store"

import styles from "./index.module.scss"

let lastScrollTop = 0

const RecordContent = () => {
  const contentRef = useRef<HTMLElement>(null)
  const [humanScroll, setHumanScroll] = useState(false)
  const [chatList, setChatList] = useState<ICommentItem[]>([])
  const meetingId = useSelector((state: RootState) => state.global.meetingId)

  useEffect(() => {
    if (!meetingId) return
    const commentsRef = collection(db, "meetings", meetingId, "comments")
    const q = query(commentsRef, orderBy("speak_at"))

    const unsubscribe = onSnapshot(q, (querySnapshot) => {
      const messageHistory: ICommentItem[] = []
      querySnapshot.forEach((doc) => {
        const data = doc.data() as ICommentItem
        data.speaker = data.speaker.toString()
        messageHistory.push(data)
      })
      setChatList(messageHistory)
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
  }, [chatList, humanScroll])

  return (
    <section className={styles.record} ref={contentRef}>
      {chatList.map((item, index) => (
        <div key={index} className={styles.item}>
          <div className={styles.left}>
            <Avatar userName={item.speaker}></Avatar>
          </div>
          <div className={styles.right}>
            <div className={styles.up}>
              <div className={styles.userName}>{item.speaker}</div>
              <div className={styles.time}>
                {new Date(item.speak_at).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </div>
            </div>
            <div className={styles.bottom}>
              <div className={styles.content}>{item.message}</div>
            </div>
          </div>
        </div>
      ))}
    </section>
  )
}

export default RecordContent
