<?xml version="1.0" encoding="UTF-8"?>
<sc version="201801" id="1" name="" frequency="1" steps="0" defaultIntergreenMatrix="0" EPICSTimeHorizon="100000" EPICSLogLevel="3" interstagesUsingMinDurations="true" checkSum="1078716222">
  <signaldisplays>
    <display id="1" name="Red" state="RED">
      <patterns>
        <pattern pattern="MINUS" color="#FF0000" isBold="true" />
      </patterns>
    </display>
    <display id="2" name="Red/Amber" state="REDAMBER">
      <patterns>
        <pattern pattern="FRAME" color="#CCCC00" isBold="true" />
        <pattern pattern="SLASH" color="#CC0000" isBold="false" />
        <pattern pattern="MINUS" color="#CC0000" isBold="false" />
      </patterns>
    </display>
    <display id="3" name="Green" state="GREEN">
      <patterns>
        <pattern pattern="FRAME" color="#00CC00" isBold="true" />
        <pattern pattern="SOLID" color="#00CC00" isBold="false" />
      </patterns>
    </display>
    <display id="4" name="Amber" state="AMBER">
      <patterns>
        <pattern pattern="FRAME" color="#CCCC00" isBold="true" />
        <pattern pattern="SLASH" color="#CCCC00" isBold="false" />
      </patterns>
    </display>
  </signaldisplays>
  <signalsequences>
    <signalsequence id="3" name="Red-Red/Amber-Green-Amber">
      <state display="1" isFixedDuration="false" isClosed="true" defaultDuration="1000" />
      <state display="2" isFixedDuration="true" isClosed="true" defaultDuration="1000" />
      <state display="3" isFixedDuration="false" isClosed="false" defaultDuration="5000" />
      <state display="4" isFixedDuration="true" isClosed="true" defaultDuration="3000" />
    </signalsequence>
    <signalsequence id="7" name="Red-Green-Amber">
      <state display="1" isFixedDuration="false" isClosed="true" defaultDuration="1000" />
      <state display="3" isFixedDuration="false" isClosed="false" defaultDuration="5000" />
      <state display="4" isFixedDuration="true" isClosed="true" defaultDuration="3000" />
    </signalsequence>
  </signalsequences>
  <sgs>
    <sg id="3" name="East entry" defaultSignalSequence="3" underEPICSControl="false">
      <defaultDurations>
        <defaultDuration display="2" duration="1000" />
        <defaultDuration display="4" duration="3000" />
        <defaultDuration display="1" duration="0" />
        <defaultDuration display="3" duration="0" />
      </defaultDurations>
    </sg>
    <sg id="6" name="South entry" defaultSignalSequence="3" underEPICSControl="false">
      <defaultDurations>
        <defaultDuration display="2" duration="1000" />
        <defaultDuration display="4" duration="3000" />
        <defaultDuration display="1" duration="0" />
        <defaultDuration display="3" duration="0" />
      </defaultDurations>
    </sg>
    <sg id="9" name="West entry" defaultSignalSequence="3" underEPICSControl="false">
      <defaultDurations>
        <defaultDuration display="2" duration="1000" />
        <defaultDuration display="4" duration="3000" />
        <defaultDuration display="1" duration="0" />
        <defaultDuration display="3" duration="0" />
      </defaultDurations>
    </sg>
    <sg id="12" name="Nord entry" defaultSignalSequence="3" underEPICSControl="false">
      <defaultDurations>
        <defaultDuration display="2" duration="1000" />
        <defaultDuration display="4" duration="3000" />
        <defaultDuration display="1" duration="0" />
        <defaultDuration display="3" duration="0" />
      </defaultDurations>
    </sg>
  </sgs>
  <intergreenmatrices />
  <progs>
    <prog id="1" cycletime="60000" switchpoint="0" offset="0" intergreens="0" fitness="0.000000" vehicleCount="0" name="Signal program">
      <sgs>
        <sg sg_id="3" signal_sequence="7">
          <cmds>
            <cmd display="3" begin="0" />
            <cmd display="1" begin="30000" />
          </cmds>
          <fixedstates>
            <fixedstate display="4" duration="1000" />
          </fixedstates>
        </sg>
        <sg sg_id="6" signal_sequence="7">
          <cmds>
            <cmd display="1" begin="0" />
            <cmd display="3" begin="30000" />
          </cmds>
          <fixedstates>
            <fixedstate display="4" duration="1000" />
          </fixedstates>
        </sg>
        <sg sg_id="9" signal_sequence="7">
          <cmds>
            <cmd display="3" begin="0" />
            <cmd display="1" begin="30000" />
          </cmds>
          <fixedstates>
            <fixedstate display="4" duration="1000" />
          </fixedstates>
        </sg>
        <sg sg_id="12" signal_sequence="7">
          <cmds>
            <cmd display="1" begin="0" />
            <cmd display="3" begin="30000" />
          </cmds>
          <fixedstates>
            <fixedstate display="4" duration="1000" />
          </fixedstates>
        </sg>
      </sgs>
    </prog>
  </progs>
  <stages>
    <stage id="1" name="Stage 1" isPseudoStage="false">
      <activations>
        <activation sg_id="3" activation="ON" />
        <activation sg_id="6" activation="ON" />
        <activation sg_id="9" activation="ON" />
        <activation sg_id="12" activation="ON" />
      </activations>
    </stage>
    <stage id="2" name="Stage 2" isPseudoStage="false">
      <activations>
        <activation sg_id="3" activation="OFF" />
        <activation sg_id="6" activation="OFF" />
        <activation sg_id="9" activation="OFF" />
        <activation sg_id="12" activation="OFF" />
      </activations>
    </stage>
  </stages>
  <interstageProgs />
  <stageProgs />
  <dailyProgLists />
</sc>