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
READ_CONTINUOUS = [dict(object="lbl_Drum_Rev_Act", widget_type ="label", read_expr="_TPA",write_var=None,
                        convert_value=lambda s: float(s) >= 0.5, fmt=None),]