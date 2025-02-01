import React from "react"
import { CloseOutlined } from "@ant-design/icons"

import styles from "./index.module.scss"

interface IExtendMessageProps {
  open?: boolean
  onClose?: () => void
}

const ExtendMessage = (props: IExtendMessageProps) => {
  const { open = false, onClose } = props

  const onClickExtend = () => {
    // window.sttManager.reStartTranscription()
    // window.rtmManager.updateSttStatus("start")
    onClose?.()
  }

  return open ? (
    <div className={styles.extendMessage}>
      <span className={styles.text}>Extend experience free text</span>
      <span className={styles.btn} onClick={onClickExtend}>
        Extend experience
      </span>
      <CloseOutlined onClick={() => onClose?.()}></CloseOutlined>
    </div>
  ) : null
}

export default ExtendMessage
