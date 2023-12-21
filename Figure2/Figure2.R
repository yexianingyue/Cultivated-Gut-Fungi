### Figure 2b
rm(list=ls())
load("fig2b.RData") # load data
fig2b <- ggplot(data=fig2b_data,aes(x=CAP1, y=CAP3, fill=subPhylum))+
    geom_point(shape=21,size=5)+
    scale_fill_manual(values=colors.subphylum)+
    theme(panel.grid.minor = element_blank(),
          text = element_text(color="black"))
ggsave("fig2b.pdf", fig2b, width=7, height=4)

### Figure 2c
rm(list=ls())
load("fig2c.RData")
fig2c <- Heatmap(data,
                 cluster_columns = F, cluster_rows = T,
                 show_row_dend = F, show_column_dend = F,
                 row_split = factor(module_group$Group, levels=module_order),
                 clustering_distance_rows  = "canberra",
                 clustering_distance_columns  = "canberra",
                 row_title_rot = 0,
                 rect_gp = gpar(col = "grey", lwd = 0.1), # 内部线条颜色
                 row_gap=unit(0,'mm'), column_gap = unit(0,'mm'), border = T,
                 row_names_gp = gpar(fontsize=5),column_names_gp = gpar(fontsize=5),
                 column_split = factor(clades_group$subPhylum, levels=subphylum_order), column_title_rot = 20,
                 col = col_legend)

### Figure 2d-eggNog
rm(list=ls())
load("fig2d-eggnog.RData")
venn = venn.diagram(
    disable.logging = T,
    x = list(a,b,c,d),
    category.names= c("Saccharomycotina (yeast)", "Pezizomycotina (filamentous fungus)", "Basidiomycota", "Mucoromycota"),
    filename = NULL,
    fill=c("#7cae00", '#f8766d', "#00bfc4", "#c77cff")
)
pdf("fig2d-ennNog.pdf", width=5.59, height=4.87)
grid.newpage()
grid.draw(venn)
dev.off()

### Figure 2d-KEGG
rm(list=ls())
load("fig2d-kegg.RData")
venn = venn.diagram(
    disable.logging = T,
    x = list(a,b,c,d),
    category.names= c("Saccharomycotina (yeast)", "Pezizomycotina (filamentous fungus)", "Basidiomycota", "Mucoromycota"),
    filename = NULL,
    fill=c("#7cae00", '#f8766d', "#00bfc4", "#c77cff")
)
pdf("fig2d-KEGG.pdf", width=5.59, height=4.87)
grid.newpage()
grid.draw(venn)
dev.off()

### Figure 2e
rm(list=ls())
load("fig2e.RData")
p <- ggplot(data, aes(x=Var1, y=value, fill=Var2))+
    geom_bar(stat="identity")+
    facet_wrap(.~Var2, ncol=1)+
    theme_bw()+
    theme(panel.grid = element_blank())+
    scale_fill_manual(values=colors.subphylum)
ggsave("fig2e.pdf", p, width=12, height=5)


