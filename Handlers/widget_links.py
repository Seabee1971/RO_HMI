
# --- Bindings registry (one source of truth) ---
# widget_type: "lineedit" (two-way) | "label" (device→UI) | "bool_pair" (device→two labels)
# read_expr: expression usable by MG (e.g., "@IN[6]", "_TPX"). None if not polled.
# write_var: Galil variable name for "var=value". None if read-only.
# convert_value: device text -> python value. fmt: python value -> display text.

WIDGET_LINKS = [
    dict(object="dsb_Back_Distance", widget_type ="doublespinbox", read_expr=None, write_var="back",
         convert_value=float, fmt=lambda v: f"{v:g}"),
    dict(object="dsb_Shift_Distance", widget_type ="doublespinbox", read_expr=None, write_var="shift",
         convert_value=float, fmt=lambda v: f"{v:g}"),
    dict(object="dsb_Offset_Distance",widget_type ="doublespinbox", read_expr=None, write_var="offset",
         convert_value=float, fmt=lambda v: f"{v:g}"),

    dict(object="lbl_Drum_Rev_Act",  widget_type ="label", read_expr="rev",  write_var=None,
         convert_value=lambda s: float(s), fmt=lambda v: f"{v:.0f}"),
    dict(object="lbl_Drum_Speed_Act",widget_type ="label", read_expr="_TDX", write_var=None,
         convert_value=lambda s: float(s), fmt=lambda v: f"{v:.2f}"),

    dict(object=("lbl_Sw1_On", "lbl_Sw1_Off"),widget_type ="bool_pair", read_expr="test", write_var=None,
         convert_value=lambda s: float(s) >= 0.5, fmt=None),
    dict(object=("lbl_Sw2_On", "lbl_Sw2_Off"),widget_type ="bool_pair", read_expr="@IN[8]", write_var=None,
         convert_value=lambda s: float(s) >= 0.5, fmt=None),
]
READ_CONTINUOUS = ('''ER,OE,CN,MT,CE,LC,PF,VF,YA,YB,YC,LinRes,EncRes,MicStep,StepRes,ActCnt,ComStps,StP_mm,SP,AC,DC''')
