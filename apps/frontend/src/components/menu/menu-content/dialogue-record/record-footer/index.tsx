import { useEffect, useRef, useMemo, useState } from "react"
import { useDispatch, useSelector } from "react-redux"
import { RootState } from "@/store"
import { useResizeObserver, formatTime } from "@/common"
import { SettingIcon } from "@/components/icons"
import axios from "axios"
import { CLOUD_RUN_ENDPOINT } from "@/config"

import styles from "./index.module.scss"

interface IRecordFooterProps {
  onClickSetting?: () => void
}

const RecordFooter = (props: IRecordFooterProps) => {
  const options = useSelector((state: RootState) => state.global.options)
  const { channel } = options
  const [isLoading, setIsLoading] = useState(false)

  const handleCallAIAgent = async () => {
    setIsLoading(true)
    try {
      const response = await axios.get(`${CLOUD_RUN_ENDPOINT}/meeting/${channel}/agent-feedback`)
      console.log(response.data)
    } catch (error) {
      console.error("Error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section className={styles.footer}>
      <div className={styles.btnWrapper}>
        <span
          className={`${styles.btnAiAgent} ${isLoading ? styles.disabled : ""}`}
          onClick={!isLoading ? handleCallAIAgent : undefined}
        >
          {isLoading ? "Loading..." : "Call AI Agent"}
        </span>
      </div>
    </section>
  )
}

export default RecordFooter
