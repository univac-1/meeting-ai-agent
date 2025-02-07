import Avatar from "@/components/avatar"
import { ICommentItem } from "@/types"
import { useRef, useEffect } from "react"
import { useSelector } from "react-redux"
import { RootState } from "@/store"
import styles from "./index.module.scss"

const RecordContent = () => {
  const contentRef = useRef<HTMLElement>(null)
  const lastMessageRef = useRef<HTMLDivElement>(null)
  const chatHistory = useSelector((state: RootState) => state.global.chatHistory)

  // chatHistory更新時に常にリストの最下部へスクロールする
  useEffect(() => {
    lastMessageRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [chatHistory])

  return (
    <section className={styles.record} ref={contentRef}>
      {chatHistory.map((item, index) => (
        <div key={index} className={styles.item}>
          <div className={styles.left}>
            <Avatar userName={item.speaker} />
          </div>
          <div className={styles.right}>
            <div className={styles.up}>
              <div className={styles.userName}>{item.speaker}</div>
              <div className={styles.time}>
                {new Date(item.speak_at).toLocaleTimeString("ja-JP", {
                  hour: "2-digit",
                  minute: "2-digit",
                  second: "2-digit",
                })}
              </div>
            </div>
            <div className={styles.bottom}>
              <div className={styles.content}>
                {item.meta && item.meta.role === "ai" ? (
                  <span className={styles.aiMessage}>{item.message}</span>
                ) : (
                  item.message
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
      <div ref={lastMessageRef} />
    </section>
  )
}

export default RecordContent
