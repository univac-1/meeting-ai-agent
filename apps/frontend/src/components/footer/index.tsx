import { MicIcon, CamIcon, MemberIcon, ConversationIcon, AiIcon, MinutesIcon } from "../icons"
import { showAIModule } from "@/common"
import { useSelector, useDispatch } from "react-redux"
import {
  setUserInfo,
  setMemberListShow,
  setDialogRecordShow,
  setCaptionShow,
  setAIShow,
  setMinutesShow,
  removeMenuItem,
  addMenuItem,
  setLocalAudioMute,
  setLocalVideoMute,
  addMessage,
  setTipSTTEnable,
} from "@/store/reducers/global"
import { RootState } from "@/store"
import { useEffect, useMemo } from "react"
import { useNavigate, useLocation } from "react-router-dom"

import styles from "./index.module.scss"

interface IFooterProps {
  style?: React.CSSProperties
}

const Footer = (props: IFooterProps) => {
  const { style } = props
  const nav = useNavigate()
  const dispatch = useDispatch()
  const location = useLocation()
  const localAudioMute = useSelector((state: RootState) => state.global.localAudioMute)
  const localVideoMute = useSelector((state: RootState) => state.global.localVideoMute)
  const memberListShow = useSelector((state: RootState) => state.global.memberListShow)
  const dialogRecordShow = useSelector((state: RootState) => state.global.dialogRecordShow)
  const captionShow = useSelector((state: RootState) => state.global.captionShow)
  const tipSTTEnable = useSelector((state: RootState) => state.global.tipSTTEnable)
  const aiShow = useSelector((state: RootState) => state.global.aiShow)
  const minutesShow = useSelector((state: RootState) => state.global.minutesShow)
  const sttData = useSelector((state: RootState) => state.global.sttData)

  useEffect(() => {
    if (tipSTTEnable) {
      setTimeout(() => {
        dispatch(setTipSTTEnable(false))
      }, 4000)
    }
  }, [tipSTTEnable])

  const hasSttStarted = useMemo(() => {
    return sttData.status === "start"
  }, [sttData])

  const MicText = useMemo(() => {
    return localAudioMute ? "UnMute Audio" : "Mute Audio"
  }, [localAudioMute])

  const CameraText = useMemo(() => {
    return localVideoMute ? "UnMute Video" : "Mute Video"
  }, [localVideoMute])

  const captionText = useMemo(() => {
    return captionShow ? "Stop CC" : "Start CC"
  }, [captionShow])

  const onClickMic = () => {
    dispatch(setLocalAudioMute(!localAudioMute))
  }

  const onClickCam = () => {
    dispatch(setLocalVideoMute(!localVideoMute))
  }

  const onClickMember = () => {
    dispatch(setMemberListShow(!memberListShow))
  }

  const onClickDialogRecord = () => {
    dispatch(setDialogRecordShow(!dialogRecordShow))
    if (dialogRecordShow) {
      dispatch(removeMenuItem("DialogRecord"))
    } else {
      dispatch(addMenuItem("DialogRecord"))
    }
  }

  const onClickCaption = () => {
    if (sttData.status !== "start") {
      return dispatch(setTipSTTEnable(true))
    }
    dispatch(setCaptionShow(!captionShow))
  }

  const onClickMinutesShow = () => {
    dispatch(setMinutesShow(!minutesShow))
    if (minutesShow) {
      dispatch(removeMenuItem("Minutes"))
    } else {
      dispatch(addMenuItem("Minutes"))
    }
  }

  const onClickAiShow = () => {
    dispatch(setAIShow(!aiShow))
    if (aiShow) {
      dispatch(removeMenuItem("AI"))
    } else {
      dispatch(addMenuItem("AI"))
    }
  }

  const onClickEnd = () => {
    if (location.search) {
      nav(`/?${location.search.slice(1)}`)
    } else {
      nav("/")
    }
    dispatch(addMessage({ content: "end meeting success!", type: "success" }))
  }

  return (
    <footer className={styles.footer} style={style}>
      <section className={styles.content}>
        {/* audio */}
        <span className={styles.item} onClick={onClickMic}>
          <MicIcon active={!localAudioMute}></MicIcon>
          <span className={styles.text}>{MicText}</span>
        </span>
        {/* video */}
        <span className={styles.item} onClick={onClickCam}>
          <CamIcon active={!localVideoMute}></CamIcon>
          <span className={styles.text}>{CameraText}</span>
        </span>
        {/* member */}
        <span className={styles.item} onClick={onClickMember}>
          <MemberIcon active={memberListShow}></MemberIcon>
          <span className={styles.text}>Participants List</span>
        </span>
        {/* dialog */}
        <span className={`${styles.item}`} onClick={onClickDialogRecord}>
          <ConversationIcon active={dialogRecordShow}></ConversationIcon>
          <span className={styles.text}>Conversation History</span>
        </span>
        {/* minutes */}
        <span className={styles.item} onClick={onClickMinutesShow}>
          <MinutesIcon active={minutesShow}></MinutesIcon>
          <span className={styles.text}>Minutes</span>
        </span>
        {/* ai */}
        {showAIModule() ? (
          <span className={styles.item} onClick={onClickAiShow}>
            <AiIcon active={aiShow}></AiIcon>
            <span className={styles.text}>AI Assistant</span>
          </span>
        ) : null}
      </section>
      <span className={styles.end} onClick={onClickEnd}>
        Close Conversation
      </span>
    </footer>
  )
}

export default Footer
