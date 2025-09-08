BINDINGS = [
    dict(object="dsb_Back_Distance",   kind="doublespinbox", read_expr=None, write_var="back",
         coerce=float, fmt=lambda v: f"{v:g}"),
    dict(object="dsb_Shift_Distance",  kind="doublespinbox", read_expr=None, write_var="shift",
         coerce=float, fmt=lambda v: f"{v:g}"),
    dict(object="dsb_Offset_Distance", kind="doublespinbox", read_expr=None, write_var="offset",
         coerce=float, fmt=lambda v: f"{v:g}"),

    dict(object="lbl_Drum_Rev_Act",   kind="label", read_expr="rev",  write_var=None,
         coerce=lambda s: float(s), fmt=lambda v: f"{v:.0f}"),
    dict(object="lbl_Drum_Speed_Act", kind="label", read_expr="_TDX", write_var=None,
         coerce=lambda s: float(s), fmt=lambda v: f"{v:.2f}"),

    dict(object=("lbl_Sw1_Grn", "lbl_Sw1_Red"), kind="bool_pair", read_expr="@IN[6]", write_var=None,
         coerce=lambda s: float(s) >= 0.5, fmt=None),
    dict(object=("lbl_Sw2_Grn", "lbl_Sw2_Red"), kind="bool_pair", read_expr="@IN[8]", write_var=None,
         coerce=lambda s: float(s) >= 0.5, fmt=None),
]
