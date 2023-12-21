library(ggplot2)


### Figure 3a
rm(list=ls())
load("fig3a.RData")
fig3a <- f1 + theme(
    legend.position = 'bottom',
    axis.text.y = element_blank(),
    axis.ticks.y = element_blank()
) +
    f2 + theme_void() + theme(axis.text.y = element_text(color = "black",hjust = 0,size = 5),
    strip.text = element_blank()) +
    scale_fill_manual(values = colors.subphylum) +
    plot_layout(widths =c(9, 1))
ggsave("fig3a.pdf",fig3a,width=12,height=10)

### Figure 3b
rm(list=ls())
load("./fig3b.RData")
fig3b <- ggplot(data = fig3b_data,
       aes(x=Axis.1,
           y=Axis.2)) +
    geom_point(aes(color=Group),size=2)+
    stat_ellipse(aes(fill=Group),size=1, geom="polygon", level=0.8, alpha=0.3)+
    labs(x="PC1(24.1%)", y = "PC2(14.4%)")+
    scale_color_manual(values=colors.subphylum)+
    scale_fill_manual(values=colors.subphylum)
fig3b
# ggsave("fig3b.pdf",fig3b,width=7.3, height=4.8)

### Figure 3c
rm(list=ls())
load("fig3c.RData")
fig3c <- ggplot(data,aes(x=x, y=y, fill=Group))+
    geom_bar(stat="identity")+
    geom_hline(yintercept = 0.7, linetype="dashed")+
    facet_grid(.~Group,scales="free_x",space="free")+
    theme_bw()+
    theme(axis.text.x=element_blank(),
          panel.grid = element_blank(),
          axis.title.x = element_blank(),
          axis.ticks.x = element_blank())+
    scale_fill_manual(values=colors.metabolome.type)+
    ylab(label="RFCV R")
fig3c
# ggsave("fig3c.pdf", widht=15, height=5)

