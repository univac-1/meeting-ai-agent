import { LoadingOutlined } from "@ant-design/icons"
import { useEffect, useRef, useMemo, useState } from "react"
import { useDispatch, useSelector } from "react-redux"
import { RootState } from "@/store"
import { useResizeObserver, formatTime } from "@/common"
import { SettingIcon } from "@/components/icons"
import axios from "axios"

import { CLOUD_RUN_ENDPOINT } from "@/config"
import { db } from "@/firebase"
import { collection, onSnapshot, orderBy, query, doc } from "firebase/firestore"
import { notification } from "antd"
import { AiIcon } from "@/components/icons"

import styles from "./index.module.scss"

interface IRecordFooterProps {
  onClickSetting?: () => void
}

const RecordFooter = (props: IRecordFooterProps) => {
  const options = useSelector((state: RootState) => state.global.options)
  const { channel } = options
  const [isLoadingGetAIOpinion, setIsLoadingGetAIOpinion] = useState(false)
  const [isLoadingCallAIAgent, setIsLoadingCallAIAgent] = useState(false)
  const [isPending, setIsPending] = useState(false)

  const meetingId = useSelector((state: RootState) => state.global.meetingId)

  useEffect(() => {
    if (!meetingId) return

    const docRef = doc(db, "meetings", meetingId);
    const unsubscribe = onSnapshot(docRef, (docSnapshot) => {
      if (docSnapshot.exists()) {
        const data = docSnapshot.data();
        console.log("ドキュメントが更新されました:", data);

        // intervention_request.statusが"pending"の場合の処理
        if (data.intervention_request?.status === "pending") {
          console.log("介入リクエストがペンディング状態になりました。");
          notification.info({
            message: "AIエージェントから意見があります",
            description: "発言を許可する場合は「Get AI's Opinion」ボタンをクリックしてください。",
            placement: "bottom",
            duration: 0,
            icon: <AiIcon></AiIcon>,
          });
          setIsPending(true);
        }
        else {
          setIsPending(false);
        }
      } else {
        console.log("ドキュメントが存在しません");
      }
    }, (error) => {
      console.error("サブスクライブ中にエラーが発生しました:", error);
    });

    return () => unsubscribe()
  }, [meetingId])

  const handleGetAIOpinion = async () => {
    setIsLoadingGetAIOpinion(true)
    try {
      const response = await axios.get(`${CLOUD_RUN_ENDPOINT}/meeting/${channel}/intervention`)
      console.log(response.data)
    } catch (error) {
      console.error("Error:", error)
    } finally {
      setIsLoadingGetAIOpinion(false)
    }
  }

  const handleCallAIAgent = async () => {
    setIsLoadingCallAIAgent(true)
    try {
      const response = await axios.get(`${CLOUD_RUN_ENDPOINT}/meeting/${channel}/agent-feedback`)
      console.log(response.data)
    } catch (error) {
      console.error("Error:", error)
    } finally {
      setIsLoadingCallAIAgent(false)
    }
  }

  return (
    <section className={styles.footer}>
      <div className={styles.btnWrapper}>
        <span
          className={`${styles.btnGetAIOpinion} ${isLoadingGetAIOpinion || !isPending ? styles.disabled : ""}`}
          onClick={!isLoadingGetAIOpinion && isPending ? handleGetAIOpinion : undefined}
        >
          {isLoadingGetAIOpinion ? <LoadingOutlined /> : "Get AI's Opinion"}
        </span>
        <span
          className={`${styles.btnCallAIAgent} ${isLoadingCallAIAgent ? styles.disabled : ""}`}
          onClick={!isLoadingCallAIAgent ? handleCallAIAgent : undefined}
        >
          {isLoadingCallAIAgent ? <LoadingOutlined /> : "Call AI Agent"}
        </span>
      </div>
    </section>
  )
}

export default RecordFooter
