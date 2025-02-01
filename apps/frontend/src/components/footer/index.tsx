import {
  MicIcon,
  CamIcon,
  MemberIcon,
  CaptionIcon,
  TranscriptionIcon,
  SettingIcon,
  AiIcon,
  ArrowUpIcon,
} from "../icons"
import { showAIModule } from "@/common"
import { useSelector, useDispatch } from "react-redux"
import {
  setUserInfo,
  setMemberListShow,
  setDialogRecordShow,
  setCaptionShow,
  setAIShow,
  removeMenuItem,
  addMenuItem,
  setLocalAudioMute,
  setLocalVideoMute,
  addMessage,
  setTipSTTEnable,
} from "@/store/reducers/global"
import LanguageSettingDialog from "../dialog/language-setting"
import AiAgentDialog from "../dialog/ai-agent"
import CaptionPopover from "./caption-popover"
import { Popover } from "antd"
import { RootState } from "@/store"
import { useEffect, useMemo, useState } from "react"
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
  const sttData = useSelector((state: RootState) => state.global.sttData)
  const [showLanguageSetting, setShowLanguageSetting] = useState(false)
  const [showAIAgent, setAIAgent] = useState(false)

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

  const onClickAiShow = () => {
    dispatch(setAIShow(!aiShow))
    if (aiShow) {
      dispatch(removeMenuItem("AI"))
    } else {
      dispatch(addMenuItem("AI"))
    }
  }

  const toggleAIAgentDialog = () => {
    setAIAgent(!showAIAgent)
  }

  const toggleLanguageSettingDialog = () => {
    setShowLanguageSetting(!showLanguageSetting)
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
        {/* caption */}
        <span
          className={`${styles.item} ${!hasSttStarted ? "disabled" : ""}`}
          onClick={onClickCaption}
        >
          <CaptionIcon disabled={!hasSttStarted} active={captionShow}></CaptionIcon>
          <span className={styles.text}>{captionText}</span>
        </span>
        <CaptionPopover>
          <span className={styles.arrowWrapper}>
            <ArrowUpIcon width={16} height={16}></ArrowUpIcon>
          </span>
        </CaptionPopover>
        {/* dialog */}
        <span className={`${styles.item}`} onClick={onClickDialogRecord}>
          <TranscriptionIcon active={dialogRecordShow}></TranscriptionIcon>
          <span className={styles.text}>Conversation History</span>
        </span>
        {/* ai agent */}
        <Popover placement="top" content="Please start transcription first" open={tipSTTEnable}>
          <span className={`${styles.item}`} onClick={toggleAIAgentDialog}>
            <AiIcon></AiIcon>
            <span className={`${styles.text}`}>AI Agent</span>
          </span>
        </Popover>
        {/* language */}
        <Popover placement="top" content="Please start transcription first" open={tipSTTEnable}>
          <span className={`${styles.item}`} onClick={toggleLanguageSettingDialog}>
            <SettingIcon></SettingIcon>
            <span className={`${styles.text}`}>Languages Setting</span>
          </span>
        </Popover>
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
      <AiAgentDialog
        open={showAIAgent}
        onOk={() => setAIAgent(false)}
        onCancel={() => setAIAgent(false)}
      ></AiAgentDialog>
    </footer>
  )
}

export default Footer
