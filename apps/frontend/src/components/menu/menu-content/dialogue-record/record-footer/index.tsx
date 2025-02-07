import { LoadingOutlined } from "@ant-design/icons"
import { useEffect, useRef, useMemo, useState } from "react"
import { useDispatch, useSelector } from "react-redux"
import { RootState } from "@/store"
import { useResizeObserver, formatTime } from "@/common"
import { SettingIcon, AiIcon } from "@/components/icons"
import axios from "axios"

import { CLOUD_RUN_ENDPOINT } from "@/config"
import { db } from "@/firebase"
import { collection, onSnapshot, orderBy, query, doc } from "firebase/firestore"
import { Button, notification, Space } from "antd"

import styles from "./index.module.scss"

interface IRecordFooterProps {
  onClickSetting?: () => void
}

const RecordFooter = (props: IRecordFooterProps) => {
  const options = useSelector((state: RootState) => state.global.options)
  const { channel } = options
  const [isLoadingCallAIAgent, setIsLoadingCallAIAgent] = useState(false)

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
