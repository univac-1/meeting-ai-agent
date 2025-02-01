import RecordContent from "./record-content"
import { RootState } from "@/store"
import { addMessage } from "@/store/reducers/global"
import { useSelector, useDispatch } from "react-redux"
import { downloadText, genContentText } from "@/common"
import LanguageShowDialog from "@/components/dialog/language-show"
import LanguageStorageDialog from "@/components/dialog/language-storage"
import RecordHeader from "./record-header"
import RecordFooter from "./record-footer"

import styles from "./index.module.scss"
import { useEffect, useMemo, useRef, useState } from "react"

interface DialogueRecordProps {
  onExport?: (value: string) => void
}

const DialogueRecord = (props: DialogueRecordProps) => {
  const { onExport } = props
  const dispatch = useDispatch()
  const sttSubtitles = useSelector((state: RootState) => state.global.sttSubtitles)
  const [openLanguageShowDialog, setOpenLanguageShowDialog] = useState(false)
  const [openLanguageStorageDialog, setOpenLanguageStorageDialog] = useState(false)

  const onClickStorage = () => {
    setOpenLanguageStorageDialog(true)
  }

  const onClickExport = () => {
    const content = genContentText(sttSubtitles)
    onExport?.(content)
    dispatch(addMessage({ type: "success", content: "Export success" }))
  }

  return (
    <div className={styles.dialogRecord}>
      <RecordHeader></RecordHeader>
      <RecordContent></RecordContent>
      <RecordFooter></RecordFooter>
    </div>
  )
}
export default DialogueRecord
