import { useDispatch, useSelector } from "react-redux"
import { RootState } from "@/store"
import { useEffect, useMemo, useRef, useState } from "react"
import { Modal, Alert, Select, Space } from "antd"
import axios from "axios"
import { CLOUD_RUN_ENDPOINT } from "../../../config"

import styles from "./index.module.scss"

interface IAiAgentDialogProps {
  open?: boolean
  onOk?: () => void
  onCancel?: () => void
}

const AiAgentDialog = (props: IAiAgentDialogProps) => {
  const { open, onOk, onCancel } = props
  const titleRef = useRef<HTMLDivElement>(null)
  const options = useSelector((state: RootState) => state.global.options)
  const { channel } = options

  const onClickBtn = async () => {
    axios
      .get(`${CLOUD_RUN_ENDPOINT}/meeting/${channel}/agent-feedback`)
      .then((response) => console.log(response.data))
      .catch((error) => console.error("Error:", error));
  }

  return (
    <Modal
      width={600}
      title={
        <div ref={titleRef} className="title">
          AI Agent
        </div>
      }
      open={open}
      footer={null}
      onOk={onOk}
      onCancel={onCancel}
    >
      <div className={styles.content}>
        <div className={styles.btnWrapper}>
          <span className={styles.btn} onClick={onClickBtn}>
            Start Facilitation
          </span>
        </div>
      </div>
    </Modal>
  )
}

export default AiAgentDialog
