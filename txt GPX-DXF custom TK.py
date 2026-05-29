import customtkinter

janela = customtkinter.CTk()
janela.title("Conversor GPX/DXF")
janela.geometry("500x380")

gpx_origem = None
dxf_destino = None

btn_arquivo = customtkinter.CTkButton(janela, text="Selecionar arquivo GPX e destino")
btn_arquivo.pack(pady=5)

lbl_arquivo = customtkinter.CTkLabel(janela, text="Nenhum arquivo selecionado")
lbl_arquivo.pack()

lbl_destino = customtkinter.CTkLabel(janela, text="Nenhum destino selecionado")
lbl_destino.pack()

var_ref = customtkinter.IntVar()

def alternar_frame():
    if var_ref.get() == 1:
        frame_ref.pack(pady=5)
    else:
        frame_ref.pack_forget()

chk_ref = customtkinter.CTkCheckBox(janela, text="Usar ponto de referência", variable=var_ref, command=alternar_frame)
chk_ref.pack(pady=5)

frame_ref = customtkinter.CTkFrame(janela)
customtkinter.CTkLabel(frame_ref, text="X:").grid(row=1, column=0, padx=5)
entry_x = customtkinter.CTkEntry(frame_ref, width=50)
entry_x.grid(row=0, column=1)

customtkinter.CTkLabel(frame_ref, text="Y:").grid(row=2, column=0, padx=5)
entry_y = customtkinter.CTkEntry(frame_ref, width=125)
entry_y.grid(row=1, column=1)

customtkinter.CTkLabel(frame_ref, text="Ponto:").grid(row=0, column=0, padx=5)
entry_ref = customtkinter.CTkEntry(frame_ref, width=125)
entry_ref.grid(row=2, column=1)

btn_converter = customtkinter.CTkButton(janela, text="Converter para DXF")
btn_converter.pack(pady=20)

janela.mainloop()