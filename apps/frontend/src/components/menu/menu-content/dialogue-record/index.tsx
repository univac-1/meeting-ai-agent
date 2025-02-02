import RecordContent from "./record-content"
import RecordFooter from "./record-footer"

import styles from "./index.module.scss"

const DialogueRecord = () => {
  return (
    <div className={styles.dialogRecord}>
      <RecordContent></RecordContent>
      <RecordFooter></RecordFooter>
    </div>
  )
}
export default DialogueRecord
