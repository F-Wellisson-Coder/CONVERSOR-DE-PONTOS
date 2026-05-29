import customtkinter

janela = customtkinter.CTk()
janela.title("Conversor GPX/DXF")
janela.geometry("500x380")

# Centralizar tudo verticalmente
janela.grid_rowconfigure(0, weight=1)
janela.grid_columnconfigure(0, weight=1)


frame_principal = customtkinter.CTkFrame(janela)
frame_principal.grid(row=0, column=0, sticky="nsew")

btn_arquivo = customtkinter.CTkButton(frame_principal, text="Selecionar arquivo GPX e destino")
btn_arquivo.pack(pady=5)

lbl_arquivo = customtkinter.CTkLabel(frame_principal, text="Nenhum arquivo selecionado")
lbl_arquivo.pack()

lbl_destino = customtkinter.CTkLabel(frame_principal, text="Nenhum destino selecionado")
lbl_destino.pack()

# Criar o Tabview e centralizar
Multiabas = customtkinter.CTkTabview(master=frame_principal, width=400, height=200)
Multiabas.pack(pady=20)

# Centralizar as abas dentro do Tabview
Multiabas._segmented_button.grid(sticky="ew")
Multiabas._segmented_button.grid_columnconfigure((0, 1), weight=1)

# Adicionar abas
Multiabas.add("CONVERTER")
Multiabas.add("MOVER")

# Aba CONVERTER
btn_converter = customtkinter.CTkButton(master=Multiabas.tab("CONVERTER"), text="Converter para DXF")
btn_converter.pack(pady=20)

# Aba MOVER
aba_mover = Multiabas.tab("MOVER")

customtkinter.CTkLabel(aba_mover, text="Ponto:").grid(row=0, column=0, padx=5, pady=5)
entry_ref = customtkinter.CTkEntry(aba_mover, width=50)
entry_ref.grid(row=0, column=1, padx=5, pady=5)

customtkinter.CTkLabel(aba_mover, text="X:").grid(row=1, column=0, padx=5, pady=5)
entry_x = customtkinter.CTkEntry(aba_mover, width=125)
entry_x.grid(row=1, column=1, padx=5, pady=5)

customtkinter.CTkLabel(aba_mover, text="Y:").grid(row=2, column=0, padx=5, pady=5)
entry_y = customtkinter.CTkEntry(aba_mover, width=125)
entry_y.grid(row=2, column=1, padx=5, pady=5)

btn_mover = customtkinter.CTkButton(aba_mover, text="Converter para DXF")
btn_mover.grid(row=3, column=1, pady=10)

janela.mainloop()