import Avatar from "@/components/avatar"
import { ICommentItem } from "@/types"
import { useMemo, useRef, useState, useEffect } from "react"
import { db } from "@/firebase"
import { collection, onSnapshot, orderBy, query } from "firebase/firestore"
import { useSelector } from "react-redux"
import { RootState } from "@/store"

import styles from "./index.module.scss"

let lastScrollTop = 0

const GOOGLE_API_KEY = import.meta.env.VITE_GOOGLE_API_KEY;

function base64ToBlob(base64Data: string, contentType: string): Blob {
  const byteCharacters = atob(base64Data);
  const byteArrays: Uint8Array[] = [];

  for (let offset = 0; offset < byteCharacters.length; offset += 512) {
    const slice = byteCharacters.slice(offset, offset + 512);

    const byteNumbers: number[] = new Array(slice.length);
    for (let i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }

    const byteArray = new Uint8Array(byteNumbers);
    byteArrays.push(byteArray);
  }

  return new Blob(byteArrays, { type: contentType });
}

const handleTextToSpeech = async (text: string): Promise<void> => {
  try {
    const response = await fetch(
      `https://texttospeech.googleapis.com/v1/text:synthesize?key=${GOOGLE_API_KEY}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          input: { text },
          voice: {
            languageCode: "ja-JP",
            ssmlGender: "NEUTRAL",
          },
          audioConfig: {
            audioEncoding: "MP3",
            speakingRate: "1.5",
            volumeGainDb: "-90.0",
          },
        }),
      }
    );

    const data = await response.json();

    if (data.audioContent) {
      const audioBlob = base64ToBlob(data.audioContent, "audio/mp3");
      const url = URL.createObjectURL(audioBlob);
      const audio = new Audio(url);
      await audio.play();
    }
  } catch (error) {
    console.error("音声合成に失敗した:", error);
  }
};

const RecordContent = () => {
  const contentRef = useRef<HTMLElement>(null)
  const [humanScroll, setHumanScroll] = useState(false)
  const [chatList, setChatList] = useState<ICommentItem[]>([])
  const meetingId = useSelector((state: RootState) => state.global.meetingId)
  const initialLoadRef = useRef(true);

  useEffect(() => {
    if (!meetingId) return
    const commentsRef = collection(db, "meetings", meetingId, "comments")
    const q = query(commentsRef, orderBy("speak_at"))

    const unsubscribe = onSnapshot(q, (querySnapshot) => {
      // 全ドキュメントからメッセージ履歴を構築
      const messageHistory: ICommentItem[] = querySnapshot.docs.map(doc => {
        const data = doc.data() as ICommentItem;
        data.speaker = data.speaker.toString();
        return data;
      });

      // 新しく追加されたドキュメントに対してのみ処理
      querySnapshot.docChanges().forEach(change => {
        if (change.type === "added") {
          const data = change.doc.data() as ICommentItem;
          data.speaker = data.speaker.toString();
          if (!initialLoadRef.current && data?.meta && data?.meta?.role === "ai") {
            handleAIComment(data);
          }
        }
      });

      // 初回読み込み完了後にフラグを更新
      if (initialLoadRef.current) {
        initialLoadRef.current = false;
      }

      setChatList(messageHistory)
    })

    return () => unsubscribe()
  }, [meetingId])

  const handleAIComment = (aiComment: ICommentItem) => {
    if (!aiComment.meta || !aiComment.meta.type) {
      console.warn("AIコメントのタイプが不明です:", aiComment);
      return;
    }

    switch (aiComment.meta.type) {
      case "evaluation":
        handleEvaluation(aiComment);
        break;
      case "summary":
        handleSummary(aiComment);
        break;
      case "feedback":
        handleFeedback(aiComment);
        break;
      default:
        console.warn("未対応のAIコメントタイプです:", aiComment.meta.type);
    }
  };

  const handleEvaluation = (aiComment: ICommentItem) => {
    console.log("評価コメントを処理します:", aiComment.message);
    // 評価に関する処理をここに追加
  };

  const handleSummary = (aiComment: ICommentItem) => {
    console.log("要約コメントを処理します:", aiComment.message);
    // 要約に関する処理をここに追加
  };

  const handleFeedback = (aiComment: ICommentItem) => {
    console.log("フィードバックコメントを処理します:", aiComment.message);
    handleTextToSpeech(aiComment.message);
    // フィードバックに関する処理をここに追加
  };

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
              <div className={styles.content}>
                {item.meta && item.meta?.role === "ai" ? (
                  <span className={styles.aiMessage}>{item.message}</span>
                ) : (
                  item.message
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
    </section>
  )
}

export default RecordContent
